from dataclasses import dataclass
from typing import List, Dict, Optional
import socket


@dataclass
class Host:
    name: str
    ip: Optional[str] = None
    group: Optional[str] = "default"
    user: Optional[str] = None

    def to_ini_line(self) -> str:
        parts = [self.name]
        if self.ip and self.ip != self.name:
            parts.append(f"ansible_host={self.ip}")
        if self.user:
            parts.append(f"ansible_user={self.user}")
        return " ".join(parts)

    def resolve_ip(self) -> Optional[str]:
        target = self.ip or self.name
        try:
            return socket.gethostbyname(target)
        except socket.error:
            return None

    @staticmethod
    def from_ini_line(line: str, group: str) -> "Host":
        parts = line.strip().split()
        name = parts[0]
        ip = None
        user = None

        for p in parts[1:]:
            if p.startswith("ansible_host="):
                ip = p.split("=", 1)[1]
            elif p.startswith("ansible_user="):
                user = p.split("=", 1)[1]

        return Host(name, ip, group, user)

    def __str__(self):
        return f"<Host {self.name} (ansible_host={self.ip}) group={self.group} user={self.user}>"


@dataclass
class HostList:
    hosts: List[Host]

    @classmethod
    def from_raw_ini(cls, hosts_by_group: Dict[str, List[str]]) -> "HostList":
        host_list = []

        for group, lines in hosts_by_group.items():
            for line in lines:
                if not line or line.startswith("#"):
                    continue
                host = Host.from_ini_line(line, group)
                host_list.append(host)
        return cls(hosts=host_list)

    def to_ini_lines_by_group(self) -> Dict[str, List[str]]:
        result: Dict[str, List[str]] = {}
        for host in self.hosts:
            result.setdefault(host.group or "default", []).append(host.to_ini_line())
        return result

    def add(self, new_host: Host) -> (bool, Optional[str]):
        existing_names = {h.name for h in self.hosts if h.group == new_host.group}
        existing_ansible_hosts = {
            h.ip for h in self.hosts if h.group == new_host.group and h.ip
        }
        resolved_existing_ips = {
            h.resolve_ip()
            for h in self.hosts
            if h.group == new_host.group and h.resolve_ip()
        }

        resolved_new_ip = new_host.resolve_ip()

        if new_host.name in existing_names:
            return False, "Nome de host já existe"
        if new_host.ip in existing_ansible_hosts or new_host.ip in existing_names:
            return False, "IP duplicado"
        if resolved_new_ip in resolved_existing_ips:
            return False, "IP resolvido duplicado"

        self.hosts.append(new_host)
        return True, None

    def __iter__(self):
        return iter(self.hosts)

    def __len__(self):
        return len(self.hosts)

    def __getitem__(self, index):
        return self.hosts[index]
