#!/usr/bin/env python
import re
import sys
import argparse
import os
import tempfile
import json
from typing import Dict, List, Optional
from dataclasses import dataclass
from collections import OrderedDict
from pathlib import Path


@dataclass
class LocationBlock:
    """Location 블록을 나타내는 데이터 클래스"""
    path: str  # location 경로 (키와 동일)
    directives: List[str]
    raw_content: str = ""


class NginxConfigManager:
    """Nginx 설정 파일의 server 블록 내 location을 경로 기반으로 관리하는 클래스"""
    
    def __init__(self, config_content: str):
        """
        Args:
            config_content: Nginx 설정 파일의 전체 내용
        """
        self.config_content = config_content
        self.server_blocks = self._parse_server_blocks()
    
    def _parse_server_blocks(self) -> List[Dict]:
        """설정에서 모든 server 블록을 파싱"""
        server_blocks = []
        
        # server 블록 찾기 (중첩된 중괄호 처리)
        pattern = r'server\s*\{'
        matches = list(re.finditer(pattern, self.config_content))
        
        for match in matches:
            start_pos = match.start()
            brace_count = 0
            pos = match.end() - 1  # '{' 위치부터 시작
            
            # 중괄호 균형을 맞춰 server 블록 끝 찾기
            while pos < len(self.config_content):
                if self.config_content[pos] == '{':
                    brace_count += 1
                elif self.config_content[pos] == '}':
                    brace_count -= 1
                    if brace_count == 0:
                        break
                pos += 1
            
            if brace_count == 0:
                server_block_content = self.config_content[start_pos:pos + 1]
                locations_dict = self._parse_locations_as_dict(server_block_content)
                
                server_blocks.append({
                    'start_pos': start_pos,
                    'end_pos': pos + 1,
                    'content': server_block_content,
                    'locations': locations_dict
                })
        
        return server_blocks
    
    def _parse_locations_as_dict(self, server_content: str) -> OrderedDict:
        """server 블록에서 location 블록들을 딕셔너리 형태로 파싱 (경로를 키로 사용)"""
        locations = OrderedDict()
        
        # location 블록 찾기
        pattern = r'location\s+([^\s{]+)\s*\{'
        matches = list(re.finditer(pattern, server_content))
        
        for match in matches:
            path = match.group(1)
            start_pos = match.start()
            brace_count = 0
            pos = match.end() - 1  # '{' 위치부터 시작
            
            # 중괄호 균형을 맞춰 location 블록 끝 찾기
            while pos < len(server_content):
                if server_content[pos] == '{':
                    brace_count += 1
                elif server_content[pos] == '}':
                    brace_count -= 1
                    if brace_count == 0:
                        break
                pos += 1
            
            if brace_count == 0:
                location_content = server_content[start_pos:pos + 1]
                
                # location 내부의 지시어들 추출
                inner_content = server_content[match.end():pos]
                directives = self._parse_directives(inner_content)
                
                # 경로를 키로 사용 (중복된 경로가 있으면 덮어쓰기)
                locations[path] = LocationBlock(
                    path=path,
                    directives=directives,
                    raw_content=location_content
                )
        
        return locations
    
    def _parse_directives(self, content: str) -> List[str]:
        """location 블록 내부의 지시어들을 파싱"""
        lines = content.split('\n')
        directives = []
        
        for line in lines:
            line = line.strip()
            # 빈 줄, 주석, 중괄호, location 라인은 제외
            if (line and 
                not line.startswith('#') and 
                line != '{' and 
                line != '}' and
                not line.startswith('location ')):
                directives.append(line)
        
        return directives
    
    def get_location_paths(self, server_index: int = 0) -> List[str]:
        """지정된 server 블록의 location 경로 목록 반환"""
        if server_index >= len(self.server_blocks):
            raise IndexError(f"Server block index {server_index} out of range")
        
        return list(self.server_blocks[server_index]['locations'].keys())
    
    def get_location(self, path: str, server_index: int = 0) -> Optional[LocationBlock]:
        """경로로 location 블록 조회"""
        if server_index >= len(self.server_blocks):
            raise IndexError(f"Server block index {server_index} out of range")
        
        locations = self.server_blocks[server_index]['locations']
        return locations.get(path)
    
    def has_location(self, path: str, server_index: int = 0) -> bool:
        """지정된 경로의 location이 존재하는지 확인"""
        if server_index >= len(self.server_blocks):
            return False
        
        return path in self.server_blocks[server_index]['locations']
    
    def get_all_locations(self, server_index: int = 0) -> OrderedDict:
        """지정된 server 블록의 모든 location 딕셔너리 반환"""
        if server_index >= len(self.server_blocks):
            raise IndexError(f"Server block index {server_index} out of range")
        
        return self.server_blocks[server_index]['locations']
    
    def set_location(self, path: str, directives: List[str], 
                    server_index: int = 0) -> 'NginxConfigManager':
        """
        location 설정 (추가 또는 수정)
        
        Args:
            path: location 경로 (키로도 사용됨)
            directives: 지시어 리스트
            server_index: 대상 server 블록 인덱스
        """
        locations_dict = {path: directives}
        return self._update_locations(locations_dict, server_index, replace_all=False)
    
    def set_locations(self, locations_dict: Dict[str, List[str]], 
                     server_index: int = 0) -> 'NginxConfigManager':
        """
        여러 location을 한번에 설정 (기존 location 유지하면서 업데이트)
        
        Args:
            locations_dict: {경로: [지시어들]} 형태
            server_index: 대상 server 블록 인덱스
        """
        return self._update_locations(locations_dict, server_index, replace_all=False)
    
    def replace_all_locations(self, locations_dict: Dict[str, List[str]], 
                             server_index: int = 0) -> 'NginxConfigManager':
        """
        모든 location을 새로운 location들로 교체
        
        Args:
            locations_dict: {경로: [지시어들]} 형태
            server_index: 대상 server 블록 인덱스
        """
        return self._update_locations(locations_dict, server_index, replace_all=True)
    
    def remove_location(self, path: str, server_index: int = 0) -> 'NginxConfigManager':
        """경로로 location 제거"""
        if server_index >= len(self.server_blocks):
            raise IndexError(f"Server block index {server_index} out of range")
        
        # 현재 locations 복사
        current_locations = self.server_blocks[server_index]['locations'].copy()
        
        # 지정된 경로 제거
        if path in current_locations:
            del current_locations[path]
        
        # 딕셔너리를 적절한 형태로 변환
        locations_dict = {}
        for location_path, location_block in current_locations.items():
            locations_dict[location_path] = location_block.directives
        
        return self._update_locations(locations_dict, server_index, replace_all=True)
    
    def remove_locations(self, paths: List[str], server_index: int = 0) -> 'NginxConfigManager':
        """여러 경로의 location들을 한번에 제거"""
        manager = self
        for path in paths:
            manager = manager.remove_location(path, server_index)
        return manager
    
    def _update_location_in_place(self, path: str, directives: List[str], 
                                 server_index: int = 0) -> 'NginxConfigManager':
        """기존 location의 내용만 업데이트하여 순서 유지"""
        if server_index >= len(self.server_blocks):
            raise IndexError(f"Server block index {server_index} out of range")
        
        server_block = self.server_blocks[server_index]
        locations = server_block['locations']
        
        if path not in locations:
            return self.set_location(path, directives, server_index)
        
        # 라인별로 처리하여 정확한 교체
        lines = self.config_content.split('\n')
        new_lines = []
        i = 0
        location_found = False
        
        while i < len(lines):
            line = lines[i]
            
            # 해당 location을 찾음
            if f'location {path}' in line and '{' in line and not location_found:
                location_found = True
                
                # 들여쓰기 추출
                base_indent = line[:line.find('location')]
                directive_indent = base_indent + "\t"
                
                # location 시작 라인 추가
                new_lines.append(line)
                i += 1
                
                # 기존 location 내용을 모두 스킵하고 새로운 지시어 추가
                brace_count = 1
                while i < len(lines) and brace_count > 0:
                    current_line = lines[i]
                    if '{' in current_line:
                        brace_count += current_line.count('{')
                    if '}' in current_line:
                        brace_count -= current_line.count('}')
                        if brace_count == 0:
                            # 닫는 중괄호 전에 지시어들 추가
                            for directive in directives:
                                new_lines.append(f"{directive_indent}{directive}")
                            # 닫는 중괄호 추가
                            new_lines.append(current_line)
                            i += 1  # 이 중괄호를 처리했으므로 다음으로 이동
                            break
                    i += 1
                continue
            
            new_lines.append(line)
            i += 1
        
        if not location_found:
            # location을 찾지 못했으면 기존 방식 사용
            return self.set_location(path, directives, server_index)
        
        new_config = '\n'.join(new_lines)
        return NginxConfigManager(new_config)
    
    def _simple_replace_location(self, path: str, directives: List[str], server_index: int) -> 'NginxConfigManager':
        """간단한 location 교체 (빈 줄 추가 없이)"""
        if server_index >= len(self.server_blocks):
            raise IndexError(f"Server block index {server_index} out of range")
        
        server_block = self.server_blocks[server_index]
        current_locations = server_block['locations'].copy()
        
        # 기존 location 업데이트
        if path in current_locations:
            current_locations[path].directives = directives
            
        # 딕셔너리를 적절한 형태로 변환
        locations_dict = {}
        for location_path, location_block in current_locations.items():
            locations_dict[location_path] = location_block.directives
        
        # replace_all=True로 하되 빈 줄 추가 로직 우회
        return self._update_locations_no_spacing(locations_dict, server_index)
    
    def _update_locations_no_spacing(self, locations_dict: Dict[str, List[str]], 
                                   server_index: int) -> 'NginxConfigManager':
        """빈 줄 추가 없이 location 업데이트"""
        if server_index >= len(self.server_blocks):
            raise IndexError(f"Server block index {server_index} out of range")
        
        server_block = self.server_blocks[server_index]
        server_content = server_block['content']
        
        # 모든 기존 location 제거
        current_locations = server_block['locations']
        for location in current_locations.values():
            server_content = server_content.replace(location.raw_content, '')
        
        # 새로운 location들 추가 (빈 줄 없이)
        new_locations_content = ""
        for path, directives in locations_dict.items():
            new_locations_content += f"\tlocation {path} {{\n"
            for directive in directives:
                new_locations_content += f"\t\t{directive}\n"
            new_locations_content += "\t}\n"
        
        # server 블록의 마지막 '}' 앞에 새로운 location들 추가 (빈 줄 없이)
        last_brace_pos = server_content.rfind('}')
        if last_brace_pos != -1:
            new_server_content = (
                server_content[:last_brace_pos] +
                new_locations_content +
                server_content[last_brace_pos:]
            )
        else:
            new_server_content = server_content + new_locations_content
        
        # 전체 설정에서 server 블록 교체
        new_config = (
            self.config_content[:server_block['start_pos']] +
            new_server_content +
            self.config_content[server_block['end_pos']:]
        )
        
        return NginxConfigManager(new_config)
    
    def _update_locations(self, locations_dict: Dict[str, List[str]], 
                         server_index: int, replace_all: bool = False) -> 'NginxConfigManager':
        """내부 메서드: location 업데이트 처리"""
        if server_index >= len(self.server_blocks):
            raise IndexError(f"Server block index {server_index} out of range")
        
        server_block = self.server_blocks[server_index]
        server_content = server_block['content']
        
        # 기존 location들 처리
        if replace_all:
            # 모든 기존 location 제거
            current_locations = server_block['locations']
            for location in current_locations.values():
                server_content = server_content.replace(location.raw_content, '')
            final_locations = OrderedDict()
        else:
            # 기존 location 유지하면서 업데이트
            final_locations = server_block['locations'].copy()
            # 업데이트되는 location만 제거
            for path in locations_dict.keys():
                if path in final_locations:
                    server_content = server_content.replace(final_locations[path].raw_content, '')
        
        # 빈 줄 정리 - 연속된 빈 줄을 하나로 축소
        server_content = self._clean_empty_lines(server_content)
        
        # 새로운 location들 추가
        new_locations_content = ""
        for path, directives in locations_dict.items():
            if new_locations_content:  # 첫 번째가 아니면 빈 줄 하나 추가
                new_locations_content += "\n"
            
            new_locations_content += f"\tlocation {path} {{\n"
            for directive in directives:
                new_locations_content += f"\t\t{directive}\n"
            new_locations_content += "\t}\n"
            
            # final_locations에 추가
            final_locations[path] = LocationBlock(
                path=path,
                directives=directives,
                raw_content=f"\tlocation {path} {{\n" + 
                          "".join(f"\t\t{directive}\n" for directive in directives) + 
                          "\t}\n"
            )
        
        # server 블록의 마지막 '}' 앞에 새로운 location들 추가
        last_brace_pos = server_content.rfind('}')
        if last_brace_pos != -1:
            # 마지막 중괄호 앞에 적절한 간격으로 추가
            before_brace = server_content[:last_brace_pos].rstrip()
            if new_locations_content:
                if before_brace and not before_brace.endswith('\n'):
                    new_server_content = before_brace + "\n\n" + new_locations_content + "\n" + server_content[last_brace_pos:]
                else:
                    new_server_content = before_brace + "\n" + new_locations_content + "\n" + server_content[last_brace_pos:]
            else:
                new_server_content = before_brace + "\n" + server_content[last_brace_pos:]
        else:
            new_server_content = server_content + new_locations_content
        
        # 최종 정리
        new_server_content = self._clean_empty_lines(new_server_content)
        
        # 전체 설정에서 server 블록 교체
        new_config = (
            self.config_content[:server_block['start_pos']] +
            new_server_content +
            self.config_content[server_block['end_pos']:]
        )
        
        return NginxConfigManager(new_config)
    
    def _clean_empty_lines(self, content: str) -> str:
        """연속된 빈 줄을 정리하는 헬퍼 메서드"""
        lines = content.split('\n')
        cleaned_lines = []
        empty_count = 0
        
        for line in lines:
            if line.strip() == '':
                empty_count += 1
                # 연속된 빈 줄은 최대 2개까지만 허용
                if empty_count <= 2:
                    cleaned_lines.append(line)
            else:
                empty_count = 0
                cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines)
    
    def get_config(self) -> str:
        """수정된 설정 내용 반환"""
        return self.config_content
    
    def save_config(self, file_path: str):
        """설정을 파일로 저장"""
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(self.config_content)
    
    def print_locations_summary(self, server_index: int = 0):
        """location 요약 정보 출력"""
        if server_index >= len(self.server_blocks):
            raise IndexError(f"Server block index {server_index} out of range")
        
        locations = self.server_blocks[server_index]['locations']
        print(f"Server {server_index} Locations:")
        print("-" * 50)
        
        for path, location in locations.items():
            print(f"Location: {path}")
            print(f"  Directives ({len(location.directives)} items):")
            for directive in location.directives:
                print(f"    {directive}")
            print()


class NginxSitesCLI:
    """Nginx Sites CLI 인터페이스"""
    
    def __init__(self):
        self.config_file = None
        self.manager = None
        self.server_index = 0
        self.state_file = os.path.join(tempfile.gettempdir(), '.nginx_sites_state.json')
        self._load_state()
    
    def _load_state(self):
        """저장된 상태 로드"""
        try:
            if os.path.exists(self.state_file):
                with open(self.state_file, 'r') as f:
                    state = json.load(f)
                    saved_config_file = state.get('config_file')
                    if saved_config_file and os.path.exists(saved_config_file):
                        self.config_file = saved_config_file
                        with open(self.config_file, 'r', encoding='utf-8') as cf:
                            content = cf.read()
                        self.manager = NginxConfigManager(content)
        except Exception:
            # 상태 로드 실패 시 무시 (첫 실행일 수 있음)
            pass
    
    def _save_state(self):
        """현재 상태 저장"""
        try:
            state = {'config_file': self.config_file}
            with open(self.state_file, 'w') as f:
                json.dump(state, f)
        except Exception:
            # 상태 저장 실패 시 무시
            pass
    
    def set_config(self, config_file: str):
        """설정 파일 설정"""
        config_path = Path(config_file)
        if not config_path.exists():
            print(f"Error: Config file '{config_file}' not found", file=sys.stderr)
            sys.exit(1)
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                content = f.read()
            self.manager = NginxConfigManager(content)
            self.config_file = str(config_path.absolute())
            self._save_state()
            print(f"Config file loaded: {config_file}")
        except Exception as e:
            print(f"Error loading config: {e}", file=sys.stderr)
            sys.exit(1)
    
    def _ensure_manager(self):
        """매니저가 초기화되었는지 확인"""
        if self.manager is None:
            print("Error: No config file set. Use 'set_config <config_file>' first.", file=sys.stderr)
            print("Example: ./nginx_sites.py set_config /etc/nginx/sites-enabled/default", file=sys.stderr)
            sys.exit(1)
    
    def list_locations(self):
        """모든 location 목록 출력"""
        self._ensure_manager()
        try:
            paths = self.manager.get_location_paths(self.server_index)
            print(f"Locations in server {self.server_index}:")
            for path in paths:
                print(f"  {path}")
        except IndexError as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)
    
    def show_location(self, path: str):
        """특정 location 상세 정보 출력"""
        self._ensure_manager()
        try:
            location = self.manager.get_location(path, self.server_index)
            if location:
                print(f"Location: {path}")
                print("Directives:")
                for directive in location.directives:
                    print(f"  {directive}")
            else:
                print(f"Location '{path}' not found")
        except IndexError as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)
    
    def add_location(self, path: str, directives: List[str] = None):
        """location 추가 (빈 location 또는 지시어 포함)"""
        self._ensure_manager()
        if directives is None:
            directives = []
        
        try:
            self.manager = self.manager.set_location(path, directives, self.server_index)
            print(f"Location '{path}' added")
            self._save_config()
        except Exception as e:
            print(f"Error adding location: {e}", file=sys.stderr)
            sys.exit(1)
    
    def delete_location(self, path: str):
        """location 삭제"""
        self._ensure_manager()
        try:
            if not self.manager.has_location(path, self.server_index):
                print(f"Location '{path}' not found")
                return
            
            self.manager = self.manager.remove_location(path, self.server_index)
            print(f"Location '{path}' deleted")
            self._save_config()
        except Exception as e:
            print(f"Error deleting location: {e}", file=sys.stderr)
            sys.exit(1)
    
    def add_directive(self, path: str, directive: str):
        """location에 지시어 추가 (순서 유지)"""
        self._ensure_manager()
        try:
            # 지시어가 세미콜론으로 끝나지 않으면 추가
            if not directive.strip().endswith(';'):
                directive = directive.strip() + ';'
            
            location = self.manager.get_location(path, self.server_index)
            if location:
                # 기존 지시어에 새 지시어 추가
                new_directives = location.directives + [directive]
                # 순서를 유지하면서 업데이트
                self.manager = self.manager._update_location_in_place(path, new_directives, self.server_index)
            else:
                # 새 location 생성
                new_directives = [directive]
                self.manager = self.manager.set_location(path, new_directives, self.server_index)
            
            print(f"Directive added to location '{path}': {directive}")
            self._save_config()
        except Exception as e:
            print(f"Error adding directive: {e}", file=sys.stderr)
            sys.exit(1)
    
    def _save_config(self):
        """설정 파일 저장"""
        if self.config_file:
            try:
                self.manager.save_config(self.config_file)
                print(f"Config saved to: {self.config_file}")
            except Exception as e:
                print(f"Error saving config: {e}", file=sys.stderr)
                sys.exit(1)
    
    def show_status(self):
        """현재 설정 상태 출력"""
        if self.config_file and os.path.exists(self.config_file):
            print(f"Current config file: {self.config_file}")
            if self.manager:
                try:
                    paths = self.manager.get_location_paths(self.server_index)
                    print(f"Server index: {self.server_index}")
                    print(f"Locations found: {len(paths)}")
                except Exception:
                    print("Config file exists but may have parsing issues")
        else:
            print("No config file set or file not found")
            print("Use: ./nginx_sites.py set_config <config_file>")
    
    def show_summary(self):
        """전체 요약 정보 출력"""
        self._ensure_manager()
        try:
            self.manager.print_locations_summary(self.server_index)
        except IndexError as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)
    
    def clear_state(self):
        """저장된 상태 정보 삭제"""
        try:
            if os.path.exists(self.state_file):
                os.remove(self.state_file)
                print("State cleared")
            else:
                print("No state to clear")
        except Exception as e:
            print(f"Error clearing state: {e}", file=sys.stderr)


def main():
    """메인 함수 - CLI 인터페이스"""
    parser = argparse.ArgumentParser(
        description='Nginx Sites Configuration Manager',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s set_config /etc/nginx/sites-enabled/default
  %(prog)s list
  %(prog)s show /
  %(prog)s add /api
  %(prog)s add /api "proxy_pass http://localhost:3000;"
  %(prog)s delete /api
  %(prog)s directive / "try_files $uri @flask_application;"
  %(prog)s summary
        """
    )
    
    parser.add_argument('--server', '-s', type=int, default=0,
                       help='Server block index (default: 0)')
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # set_config 명령
    set_config_parser = subparsers.add_parser('set_config', help='Set nginx config file')
    set_config_parser.add_argument('config_file', help='Path to nginx config file')
    
    # list 명령
    subparsers.add_parser('list', help='List all locations')
    
    # show 명령
    show_parser = subparsers.add_parser('show', help='Show location details')
    show_parser.add_argument('path', help='Location path')
    
    # add 명령
    add_parser = subparsers.add_parser('add', help='Add location')
    add_parser.add_argument('path', help='Location path')
    add_parser.add_argument('directive', nargs='?', help='Optional directive to add')
    
    # delete 명령
    delete_parser = subparsers.add_parser('delete', help='Delete location')
    delete_parser.add_argument('path', help='Location path')
    
    # directive 명령
    directive_parser = subparsers.add_parser('directive', help='Add directive to location')
    directive_parser.add_argument('path', help='Location path')
    directive_parser.add_argument('directive', help='Directive to add')
    
    # summary 명령
    subparsers.add_parser('summary', help='Show locations summary')
    
    # status 명령
    subparsers.add_parser('status', help='Show current configuration status')
    
    # clear 명령
    subparsers.add_parser('clear', help='Clear saved state')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    cli = NginxSitesCLI()
    cli.server_index = args.server
    
    try:
        if args.command == 'set_config':
            cli.set_config(args.config_file)
        elif args.command == 'list':
            cli.list_locations()
        elif args.command == 'show':
            cli.show_location(args.path)
        elif args.command == 'add':
            if args.directive:
                cli.add_location(args.path, [args.directive])
            else:
                cli.add_location(args.path)
        elif args.command == 'delete':
            cli.delete_location(args.path)
        elif args.command == 'directive':
            cli.add_directive(args.path, args.directive)
        elif args.command == 'summary':
            cli.show_summary()
        elif args.command == 'status':
            cli.show_status()
        elif args.command == 'clear':
            cli.clear_state()
    except KeyboardInterrupt:
        print("\nOperation cancelled")
        sys.exit(1)
