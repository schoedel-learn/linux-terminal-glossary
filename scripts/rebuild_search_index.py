#!/usr/bin/env python3
"""Rebuild commands.json and search_index.json for the glossary."""

from __future__ import annotations

import json
import math
import re
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
COMMANDS_PATH = ROOT / "commands.json"
SEARCH_INDEX_PATH = ROOT / "search_index.json"
TOKEN_RE = re.compile(r"[a-z0-9][a-z0-9\-\.]*[a-z0-9]|[a-z0-9]")


def tokenize(text: str) -> list[str]:
    return TOKEN_RE.findall(text.lower())


def tooltip_for(cmd: str, desc: str) -> str:
    desc = desc.rstrip(".")
    if desc:
        desc = desc[0].lower() + desc[1:]
    return f"Use `{cmd}` to {desc}. Helpful when you need this quickly on a Linux server."


def entry(category: str, cmd: str, desc: str, tooltip: str | None = None) -> dict[str, object]:
    return {
        "category": category,
        "cmd": cmd,
        "desc": desc,
        "tooltip": tooltip or tooltip_for(cmd, desc),
    }


EXTRA_COMMANDS = [
    # Firewall, access control, and security
    entry("VPS Management", "ufw enable", "enable the uncomplicated firewall"),
    entry("VPS Management", "ufw status verbose", "show firewall status and active rules"),
    entry("VPS Management", "ufw allow 22/tcp", "allow SSH through the firewall"),
    entry("VPS Management", "ufw allow 80,443/tcp", "allow HTTP and HTTPS through the firewall"),
    entry("VPS Management", "ufw deny 23/tcp", "block Telnet on the firewall"),
    entry("VPS Management", "ufw delete allow 22/tcp", "remove a firewall allow rule"),
    entry("VPS Management", "ufw reload", "reload firewall rules without rebooting"),
    entry("VPS Management", "ufw reset", "reset firewall rules back to defaults"),
    entry("VPS Management", "firewall-cmd --state", "check whether firewalld is running"),
    entry("VPS Management", "firewall-cmd --list-all", "list all firewalld rules for the current zone"),
    entry("VPS Management", "firewall-cmd --add-service=http --permanent", "permanently allow HTTP in firewalld"),
    entry("VPS Management", "firewall-cmd --reload", "reload firewalld after rule changes"),
    entry("VPS Management", "nft list ruleset", "list the entire nftables ruleset"),
    entry("VPS Management", "nft add table inet filter", "create a new nftables filter table"),
    entry("VPS Management", "nft flush ruleset", "remove all nftables rules"),
    entry("VPS Management", "iptables -L -n -v", "list iptables rules with counters and no DNS lookups"),
    entry("VPS Management", "iptables-save", "dump the current iptables ruleset"),
    entry("VPS Management", "fail2ban-client status", "show jail status for fail2ban"),
    entry("VPS Management", "fail2ban-client status sshd", "show details for the SSH fail2ban jail"),
    entry("VPS Management", "fail2ban-client set sshd unbanip 1.2.3.4", "remove an IP from a fail2ban jail"),
    entry("VPS Management", "lynis audit system", "run a full security audit"),
    entry("VPS Management", "rkhunter --check", "scan for rootkits with rkhunter"),
    entry("VPS Management", "chkrootkit", "scan for common rootkits"),
    entry("VPS Management", "clamscan -r /var/www", "scan a directory recursively for malware"),
    entry("VPS Management", "freshclam", "update ClamAV signatures"),
    entry("VPS Management", "auditctl -l", "list auditd rules"),
    entry("VPS Management", "ausearch -k sshd", "search audit logs by key"),
    entry("VPS Management", "aureport -au", "show an audit report for authentication events"),
    entry("VPS Management", "aa-status", "show AppArmor status"),
    entry("VPS Management", "aa-enforce /etc/apparmor.d/usr.sbin.nginx", "put an AppArmor profile into enforce mode"),
    entry("VPS Management", "getenforce", "show current SELinux mode"),
    entry("VPS Management", "setenforce 1", "switch SELinux to enforcing mode"),
    entry("VPS Management", "sestatus", "show detailed SELinux status"),
    entry("VPS Management", "semanage port -l", "list SELinux port labels"),
    entry("VPS Management", "restorecon -Rv /var/www", "restore SELinux contexts recursively"),
    entry("VPS Management", "chcon -t httpd_sys_content_t /srv/site", "temporarily change an SELinux file context"),
    entry("VPS Management", "getcap -r / 2>/dev/null", "list Linux file capabilities"),
    entry("VPS Management", "setcap cap_net_bind_service=+ep /usr/local/bin/app", "allow a binary to bind privileged ports"),
    entry("VPS Management", "unshare -n bash", "start a shell in a new network namespace"),
    entry("VPS Management", "nsenter --target 1234 --mount --uts --ipc --net --pid", "enter the namespaces of another process"),
    entry("VPS Management", "debsums -s", "check installed package files for checksum mismatches"),
    entry("VPS Management", "debscan", "list known security issues for installed packages"),
    entry("VPS Management", "needrestart -r a", "restart services after package upgrades"),
    entry("Package Management - APT/Ubuntu", "unattended-upgrade -d", "run unattended upgrades in debug mode"),
    entry("Package Management - APT/Ubuntu", "apt-mark hold nginx", "prevent a package from being upgraded"),
    entry("Package Management - APT/Ubuntu", "apt-mark unhold nginx", "allow a held package to upgrade again"),
    # Time, sessions, and service diagnostics
    entry("System Services & Systemd", "timedatectl status", "show system time, timezone, and NTP state"),
    entry("System Services & Systemd", "timedatectl set-ntp true", "enable network time synchronization"),
    entry("System Services & Systemd", "chronyc tracking", "show Chrony time sync status"),
    entry("System Services & Systemd", "chronyc sources -v", "list Chrony time sources"),
    entry("System Services & Systemd", "chronyc makestep", "force an immediate time correction"),
    entry("System Services & Systemd", "ntpq -p", "show NTP peers and offsets"),
    entry("System Services & Systemd", "ntpstat", "print concise NTP synchronization status"),
    entry("System Services & Systemd", "hostnamectl status", "show hostname and OS metadata"),
    entry("System Services & Systemd", "localectl status", "show locale and keyboard settings"),
    entry("System Services & Systemd", "loginctl list-sessions", "list active logind sessions"),
    entry("System Services & Systemd", "loginctl show-session 2", "inspect one logind session"),
    entry("System Services & Systemd", "coredumpctl list", "list captured crash dumps"),
    entry("System Services & Systemd", "coredumpctl info nginx", "show details for a captured crash dump"),
    entry("System Services & Systemd", "systemd-analyze blame", "show slowest systemd units during boot"),
    entry("System Services & Systemd", "systemd-analyze critical-chain", "show the boot dependency chain"),
    entry("System Services & Systemd", "systemd-cgls", "display the systemd cgroup tree"),
    entry("System Services & Systemd", "systemd-cgtop", "show resource usage by cgroup"),
    entry("System Services & Systemd", "systemctl daemon-reload", "reload systemd unit files after edits"),
    entry("System Services & Systemd", "systemctl is-enabled nginx", "check whether a service starts on boot"),
    entry("System Services & Systemd", "systemctl list-timers", "list active systemd timers"),
    entry("System Services & Systemd", "systemctl edit nginx", "create or edit a systemd drop-in override"),
    entry("System Services & Systemd", "journalctl -p err -b", "show errors from the current boot"),
    entry("System Services & Systemd", "journalctl --disk-usage", "show journal disk usage"),
    entry("System Services & Systemd", "journalctl -u nginx -f", "follow logs for one systemd service"),
    # Storage, filesystems, LVM, RAID, and encryption
    entry("Disk & Filesystem", "lsblk -f", "list block devices with filesystem and UUID data"),
    entry("Disk & Filesystem", "findmnt", "show all mounted filesystems"),
    entry("Disk & Filesystem", "mount -a", "mount everything from /etc/fstab"),
    entry("Disk & Filesystem", "umount -l /mnt/data", "lazy-unmount a busy filesystem"),
    entry("Disk & Filesystem", "df -i", "show inode usage by filesystem"),
    entry("Disk & Filesystem", "du -xhd1 /var", "show top-level disk usage without crossing filesystems"),
    entry("Disk & Filesystem", "ncdu /var", "browse directory disk usage interactively"),
    entry("Disk & Filesystem", "blkid", "list block device UUIDs and filesystem types"),
    entry("Disk & Filesystem", "findmnt -no SOURCE,TARGET,FSTYPE /var", "show the source device and type for one mount"),
    entry("Disk & Filesystem", "fsck -f /dev/sdb1", "force a filesystem check"),
    entry("Disk & Filesystem", "tune2fs -l /dev/sdb1", "show ext filesystem settings"),
    entry("Disk & Filesystem", "dumpe2fs -h /dev/sdb1", "print ext filesystem superblock details"),
    entry("Disk & Filesystem", "filefrag -v /var/lib/postgresql/data/base/1/12345", "inspect file fragmentation"),
    entry("Disk & Filesystem", "smartctl -a /dev/sda", "show SMART health information for a disk"),
    entry("Disk & Filesystem", "badblocks -sv /dev/sdb", "scan a disk for bad sectors"),
    entry("Disk & Filesystem", "hdparm -I /dev/sda", "show drive identity and capabilities"),
    entry("Disk & Filesystem", "ioping -c 10 /var", "measure storage latency for a path"),
    entry("Disk & Filesystem", "fio --name=randread --filename=/tmp/fio.test --size=1G --rw=randread", "benchmark random read performance"),
    entry("Disk & Filesystem", "swapon --show", "show active swap devices and files"),
    entry("Disk & Filesystem", "swapoff -a", "disable all swap devices and files"),
    entry("Disk & Filesystem", "btrfs filesystem df /", "show Btrfs space usage"),
    entry("Disk & Filesystem", "btrfs subvolume list /", "list Btrfs subvolumes"),
    entry("Disk & Filesystem", "btrfs scrub status /", "show Btrfs scrub progress"),
    entry("Disk & Filesystem", "btrfs scrub start -Bd /", "start and wait for a Btrfs scrub"),
    entry("Disk & Filesystem", "btrfs balance status /", "show Btrfs balance status"),
    entry("Disk & Filesystem", "btrfs balance start /", "start a Btrfs balance operation"),
    entry("Disk & Filesystem", "xfs_info /mnt/data", "show XFS geometry information"),
    entry("Disk & Filesystem", "xfs_repair /dev/sdb1", "repair an XFS filesystem"),
    entry("Disk & Filesystem", "xfs_growfs /mnt/data", "grow an XFS filesystem after extending storage"),
    entry("Disk & Filesystem", "cryptsetup luksFormat /dev/sdb1", "initialize a LUKS-encrypted device"),
    entry("Disk & Filesystem", "cryptsetup luksOpen /dev/sdb1 securedata", "open an encrypted LUKS device"),
    entry("Disk & Filesystem", "cryptsetup luksClose securedata", "close an opened LUKS mapping"),
    entry("Disk & Filesystem", "cryptsetup status securedata", "show status for an open LUKS mapping"),
    entry("Disk & Filesystem", "cryptsetup luksDump /dev/sdb1", "show LUKS metadata and key slots"),
    entry("Disk & Filesystem", "pvs", "list physical volumes"),
    entry("Disk & Filesystem", "vgs", "list volume groups"),
    entry("Disk & Filesystem", "lvs", "list logical volumes"),
    entry("Disk & Filesystem", "pvcreate /dev/sdb", "initialize a disk as an LVM physical volume"),
    entry("Disk & Filesystem", "vgcreate vgdata /dev/sdb", "create a new LVM volume group"),
    entry("Disk & Filesystem", "lvcreate -L 50G -n lvdata vgdata", "create a new logical volume"),
    entry("Disk & Filesystem", "lvextend -L +20G /dev/vgdata/lvdata", "extend a logical volume"),
    entry("Disk & Filesystem", "resize2fs /dev/vgdata/lvdata", "grow an ext filesystem after extending the volume"),
    entry("Disk & Filesystem", "lvreduce -L 20G /dev/vgdata/lvdata", "shrink a logical volume"),
    entry("Disk & Filesystem", "vgextend vgdata /dev/sdc", "add a disk to an existing volume group"),
    entry("Disk & Filesystem", "pvmove /dev/sdb", "move extents off one physical volume"),
    entry("Disk & Filesystem", "vgremove vgdata", "remove an LVM volume group"),
    entry("Disk & Filesystem", "lvremove /dev/vgdata/lvdata", "remove a logical volume"),
    entry("Disk & Filesystem", "vgscan", "scan for volume groups"),
    entry("Disk & Filesystem", "lvscan", "scan for logical volumes"),
    entry("Disk & Filesystem", "mdadm --detail /dev/md0", "show RAID array details"),
    entry("Disk & Filesystem", "mdadm --create /dev/md0 --level=1 --raid-devices=2 /dev/sdb /dev/sdc", "create a RAID1 array"),
    entry("Disk & Filesystem", "mdadm --examine /dev/sdb", "show RAID metadata on a device"),
    entry("Disk & Filesystem", "cat /proc/mdstat", "show Linux software RAID status"),
    # Networking, routing, VPN, and file sharing
    entry("Networking", "ss -tulpn", "list listening TCP and UDP sockets with processes"),
    entry("Networking", "lsof -i -P -n", "list open network sockets without DNS lookups"),
    entry("Networking", "ip -br address", "show IP addresses in a brief format"),
    entry("Networking", "ip route", "show the main routing table"),
    entry("Networking", "ip rule show", "show policy routing rules"),
    entry("Networking", "resolvectl status", "show DNS resolver configuration and state"),
    entry("Networking", "nmcli connection show", "list NetworkManager connections"),
    entry("Networking", "netplan apply", "apply Netplan network configuration"),
    entry("Networking", "vnstat -d", "show daily bandwidth statistics"),
    entry("Networking", "iptraf-ng", "watch live network traffic interactively"),
    entry("Networking", "tcptrack -i eth0", "watch active TCP connections on an interface"),
    entry("Networking", "mtr example.com", "run a combined ping and traceroute"),
    entry("Networking", "tcpdump -ni eth0 port 80", "capture traffic on an interface without name lookups"),
    entry("Networking", "bridge link", "show Linux bridge member interfaces"),
    entry("Networking", "brctl show", "show bridge devices with bridge-utils"),
    entry("Networking", "ip link add br0 type bridge", "create a Linux bridge"),
    entry("Networking", "ip link add link eth0 name eth0.100 type vlan id 100", "create a VLAN subinterface"),
    entry("Networking", "ovs-vsctl show", "show Open vSwitch configuration"),
    entry("Networking", "wg show", "show WireGuard peers and transfer state"),
    entry("Networking", "wg genkey", "generate a WireGuard private key"),
    entry("Networking", "wg pubkey", "derive a WireGuard public key from a private key"),
    entry("Networking", "wg showconf wg0", "show the running WireGuard config for an interface"),
    entry("Networking", "openvpn --config client.ovpn", "start an OpenVPN client from a config file"),
    entry("Networking", "exportfs -rav", "re-export all NFS shares"),
    entry("Networking", "showmount -e server", "list NFS exports from a server"),
    entry("Networking", "rpcinfo -p server", "list RPC services exposed by a host"),
    entry("Networking", "mount -t nfs server:/share /mnt/share", "mount an NFS share"),
    entry("Networking", "smbclient -L //server -N", "list Samba shares on a server"),
    entry("Networking", "testparm", "validate Samba configuration"),
    entry("Networking", "smbstatus", "show active Samba sessions and locks"),
    entry("Networking", "nmblookup server", "query NetBIOS names"),
    entry("Networking", "pdbedit -L", "list Samba users from the passdb"),
    entry("Networking", "smbpasswd -a alice", "add or update a Samba user password"),
    # Users, permissions, and process control
    entry("User & Group Management", "w", "show logged-in users and what they are doing"),
    entry("User & Group Management", "who -a", "show detailed logged-in user information"),
    entry("User & Group Management", "last -a", "show login history with remote host at the end"),
    entry("User & Group Management", "lastlog", "show the last login for every user"),
    entry("User & Group Management", "faillog", "show failed login counters"),
    entry("User & Group Management", "getent passwd alice", "query the passwd database for one user"),
    entry("User & Group Management", "getent group sudo", "query the group database for one group"),
    entry("User & Group Management", "usermod -aG sudo alice", "add a user to the sudo group"),
    entry("User & Group Management", "passwd -l alice", "lock a user account password"),
    entry("User & Group Management", "passwd -u alice", "unlock a user account password"),
    entry("User & Group Management", "chage -l alice", "show password aging information for a user"),
    entry("User & Group Management", "chage -M 90 alice", "set a password max age in days"),
    entry("User & Group Management", "pwck", "check passwd and shadow file integrity"),
    entry("User & Group Management", "grpck", "check group file integrity"),
    entry("User & Group Management", "vipw", "edit /etc/passwd safely with locking"),
    entry("User & Group Management", "vigr", "edit /etc/group safely with locking"),
    entry("User & Group Management", "visudo -c", "validate sudoers configuration"),
    entry("User & Group Management", "sudo -l", "list commands the current user may run with sudo"),
    entry("Process Management", "pgrep -af nginx", "find matching processes with full command lines"),
    entry("Process Management", "pkill -f gunicorn", "kill processes by matching the full command line"),
    entry("Process Management", "fuser -v 80/tcp", "show which process is using a port"),
    entry("Process Management", "renice -n 10 -p 1234", "change CPU scheduling priority for a process"),
    entry("Process Management", "pidstat 1", "show per-process CPU and I/O statistics continuously"),
    entry("Process Management", "vmstat 1", "show memory, CPU, and scheduler statistics continuously"),
    entry("Process Management", "mpstat -P ALL 1", "show CPU usage for every core"),
    entry("Process Management", "iostat -xz 1", "show CPU and block-device I/O utilization"),
    entry("Process Management", "sar -u 1 5", "sample CPU usage with sysstat"),
    entry("Process Management", "atop", "open an advanced interactive system monitor"),
    entry("Process Management", "glances", "open a broad interactive system monitor"),
    entry("Process Management", "nmon", "open the nmon performance monitor"),
    entry("Process Management", "perf stat -p 1234", "collect performance counters for a process"),
    entry("Process Management", "perf top", "show hot CPU code paths live"),
    entry("Process Management", "perf record -p 1234 -- sleep 30", "record CPU profiling data for a process"),
    entry("Process Management", "perf report", "read a saved perf profile report"),
    entry("Process Management", "bpftrace -l 'tracepoint:*'", "list available BPF tracepoints"),
    entry("Process Management", "sysdig", "capture and inspect system activity"),
    entry("Process Management", "stress-ng --cpu 4 --timeout 60", "stress-test CPU resources"),
    entry("Process Management", "stress --vm 2 --timeout 60", "stress-test memory allocation"),
    # Web, certificates, services, mail, and application runtimes
    entry("VPS Management", "certbot --nginx -d example.com", "obtain a Let's Encrypt certificate with the nginx plugin"),
    entry("VPS Management", "certbot --apache -d example.com", "obtain a Let's Encrypt certificate with the Apache plugin"),
    entry("VPS Management", "certbot renew --dry-run", "test certificate renewal"),
    entry("VPS Management", "certbot certificates", "list managed certificates"),
    entry("VPS Management", "certbot delete --cert-name example.com", "delete a managed certificate"),
    entry("VPS Management", "openssl s_client -connect example.com:443 -servername example.com", "inspect a live TLS handshake and certificate chain"),
    entry("VPS Management", "openssl req -new -newkey rsa:4096 -nodes -keyout server.key -out server.csr", "generate a private key and CSR"),
    entry("VPS Management", "openssl x509 -in server.crt -text -noout", "inspect certificate contents"),
    entry("VPS Management", "openssl verify -CAfile chain.pem server.crt", "verify a certificate against a CA chain"),
    entry("VPS Management", "openssl pkcs12 -info -in bundle.p12", "inspect a PKCS#12 bundle"),
    entry("VPS Management", "nginx -t", "test nginx configuration syntax"),
    entry("VPS Management", "nginx -s reload", "reload nginx without dropping connections"),
    entry("VPS Management", "apache2ctl configtest", "test Apache configuration syntax"),
    entry("VPS Management", "apache2ctl -S", "show Apache virtual host mapping"),
    entry("VPS Management", "a2ensite example.conf", "enable an Apache site"),
    entry("VPS Management", "a2dissite example.conf", "disable an Apache site"),
    entry("VPS Management", "a2enmod rewrite", "enable an Apache module"),
    entry("VPS Management", "php-fpm8.2 -t", "test PHP-FPM configuration"),
    entry("VPS Management", "supervisorctl status", "show process status from Supervisor"),
    entry("VPS Management", "supervisorctl restart all", "restart all Supervisor-managed processes"),
    entry("VPS Management", "postfix status", "check Postfix service status"),
    entry("VPS Management", "postfix reload", "reload Postfix after configuration changes"),
    entry("VPS Management", "mailq", "show queued mail"),
    entry("VPS Management", "postqueue -p", "print the Postfix mail queue"),
    entry("VPS Management", "postsuper -d ALL", "delete all messages from the Postfix queue"),
    entry("VPS Management", "postconf -n", "show non-default Postfix settings"),
    entry("VPS Management", "mail -s 'test' admin@example.com", "send a quick test email"),
    entry("VPS Management", "mutt", "open the mutt terminal mail client"),
    # Databases and backups
    entry("VPS Management", "redis-cli ping", "test connectivity to Redis"),
    entry("VPS Management", "redis-cli info memory", "show Redis memory information"),
    entry("VPS Management", "redis-cli monitor", "watch every command hitting Redis"),
    entry("VPS Management", "redis-cli save", "force a Redis RDB snapshot"),
    entry("VPS Management", "redis-cli flushdb", "delete all keys in the current Redis database"),
    entry("VPS Management", "redis-cli latency doctor", "show Redis latency analysis"),
    entry("VPS Management", "mysqlcheck --all-databases", "check all MySQL tables"),
    entry("VPS Management", "mysqloptimize --all-databases", "optimize all MySQL tables"),
    entry("VPS Management", "pg_basebackup -D /backups/pgbase -Fp -Xs -P", "take a base backup from PostgreSQL"),
    entry("VPS Management", "pg_lsclusters", "list PostgreSQL clusters on Debian and Ubuntu"),
    entry("VPS Management", "mongodump --out /backups/mongo", "dump MongoDB data to a directory"),
    entry("VPS Management", "mongorestore /backups/mongo", "restore a MongoDB dump"),
    entry("VPS Management", "restic init", "initialize a new Restic repository"),
    entry("VPS Management", "restic backup /etc /var/www", "back up paths with Restic"),
    entry("VPS Management", "restic snapshots", "list Restic snapshots"),
    entry("VPS Management", "restic restore latest --target /restore", "restore the latest Restic snapshot"),
    entry("VPS Management", "restic check", "verify repository integrity with Restic"),
    entry("VPS Management", "restic forget --keep-daily 7 --prune", "expire old Restic snapshots and prune data"),
    entry("VPS Management", "duplicity /etc file:///backup/duplicity", "back up data with Duplicity"),
    entry("VPS Management", "ddrescue /dev/sdb image.dd rescue.log", "recover data from a failing disk"),
    entry("VPS Management", "testdisk", "recover lost partitions and files interactively"),
    entry("VPS Management", "lnav /var/log/syslog", "open logs in a log-focused viewer"),
    entry("VPS Management", "multitail -f /var/log/syslog /var/log/auth.log", "tail multiple log files together"),
    entry("VPS Management", "goaccess access.log -o report.html", "analyze web access logs into a report"),
    entry("VPS Management", "logwatch --detail High --service all --range today", "generate a daily log summary"),
    entry("VPS Management", "pflogsumm /var/log/mail.log", "summarize Postfix mail logs"),
    # Automation, containers, and virtualization
    entry("VPS Management", "ansible all -m ping", "test Ansible connectivity to all hosts"),
    entry("VPS Management", "ansible-playbook site.yml", "run an Ansible playbook"),
    entry("VPS Management", "ansible-inventory --list", "print resolved Ansible inventory"),
    entry("VPS Management", "ansible-vault encrypt secrets.yml", "encrypt a file with Ansible Vault"),
    entry("VPS Management", "ansible-galaxy install -r requirements.yml", "install required Ansible roles or collections"),
    entry("VPS Management", "terraform init", "initialize a Terraform working directory"),
    entry("VPS Management", "terraform plan", "preview Terraform changes"),
    entry("VPS Management", "terraform apply", "apply Terraform infrastructure changes"),
    entry("VPS Management", "terraform destroy", "destroy Terraform-managed infrastructure"),
    entry("VPS Management", "puppet apply site.pp", "apply a Puppet manifest locally"),
    entry("VPS Management", "podman ps", "list running Podman containers"),
    entry("VPS Management", "buildah bud -t app:latest .", "build a container image with Buildah"),
    entry("VPS Management", "skopeo inspect docker://docker.io/library/nginx:latest", "inspect a remote container image"),
    entry("VPS Management", "kubectl get pods -A", "list pods in all Kubernetes namespaces"),
    entry("VPS Management", "kubectl describe pod mypod -n default", "show detailed information about a pod"),
    entry("VPS Management", "kubectl logs deploy/web -n default", "show logs from a deployment"),
    entry("VPS Management", "kubectl exec -it deploy/web -n default -- sh", "open a shell in a Kubernetes workload"),
    entry("VPS Management", "kubectl apply -f manifest.yaml", "apply Kubernetes manifest changes"),
    entry("VPS Management", "kubectl delete -f manifest.yaml", "delete resources from a Kubernetes manifest"),
    entry("VPS Management", "kubectl scale deploy/web --replicas=3", "scale a Kubernetes deployment"),
    entry("VPS Management", "kubectl rollout status deploy/web", "wait for a deployment rollout"),
    entry("VPS Management", "helm list -A", "list Helm releases in all namespaces"),
    entry("VPS Management", "helm install web chart/ -n default", "install a Helm chart"),
    entry("VPS Management", "helm upgrade web chart/ -n default", "upgrade a Helm release"),
    entry("VPS Management", "helm rollback web 1 -n default", "roll back a Helm release"),
    entry("VPS Management", "helm uninstall web -n default", "remove a Helm release"),
    entry("VPS Management", "lxc list", "list LXC containers"),
    entry("VPS Management", "lxc start web01", "start an LXC container"),
    entry("VPS Management", "lxc stop web01", "stop an LXC container"),
    entry("VPS Management", "lxc exec web01 -- bash", "open a shell inside an LXC container"),
    entry("VPS Management", "virsh list --all", "list virtual machines managed by libvirt"),
    entry("VPS Management", "virsh dominfo web01", "show libvirt guest details"),
    entry("VPS Management", "virt-install --name web01 --memory 2048 --vcpus 2 --disk size=20 --cdrom image.iso", "create a VM with virt-install"),
    entry("VPS Management", "qemu-img info disk.qcow2", "show metadata about a disk image"),
    entry("VPS Management", "qemu-img create -f qcow2 disk.qcow2 20G", "create a new QCOW2 disk image"),
]


SEARCH_SYNONYMS = {
    "memory": ["free", "vmstat", "top", "htop", "smem", "pidstat"],
    "ram": ["free", "vmstat", "top", "htop", "smem"],
    "swap": ["swapon", "swapoff", "free", "vmstat"],
    "cpu": ["top", "htop", "mpstat", "sar", "uptime", "pidstat", "perf"],
    "cpu usage": ["top", "htop", "mpstat", "sar", "pidstat"],
    "cpu load": ["uptime", "top", "vmstat", "sar"],
    "performance": ["top", "htop", "atop", "glances", "pidstat", "perf", "bpftrace", "sysdig"],
    "disk space": ["df", "du", "ncdu", "lsblk", "findmnt"],
    "disk usage": ["df", "du", "ncdu", "findmnt"],
    "disk inodes": ["df -i", "find", "stat"],
    "disk health": ["smartctl", "badblocks", "fsck", "dmesg", "hdparm"],
    "filesystem": ["lsblk", "findmnt", "mount", "umount", "blkid", "fsck", "btrfs", "xfs_info"],
    "mount disk": ["mount", "umount", "findmnt", "lsblk"],
    "encrypted disk": ["cryptsetup", "lsblk", "blkid"],
    "lvm": ["pvs", "vgs", "lvs", "pvcreate", "vgcreate", "lvcreate", "lvextend"],
    "logical volume": ["pvs", "vgs", "lvs", "lvcreate", "lvextend", "vgcreate"],
    "raid": ["mdadm", "cat /proc/mdstat"],
    "btrfs": ["btrfs", "findmnt", "lsblk"],
    "xfs": ["xfs_info", "xfs_repair", "xfs_growfs"],
    "iops": ["iostat", "iotop", "fio", "ioping"],
    "firewall": ["ufw", "iptables", "nft", "firewall-cmd", "fail2ban-client"],
    "allow port": ["ufw allow", "firewall-cmd", "iptables", "nft"],
    "block ip": ["ufw deny", "iptables", "nft", "fail2ban-client"],
    "open ports": ["ss", "lsof", "netstat", "nmap"],
    "listening ports": ["ss", "lsof", "netstat"],
    "process using port": ["lsof", "fuser", "ss"],
    "open files on port": ["lsof", "fuser", "ss"],
    "network stats": ["vnstat", "iptraf-ng", "tcptrack", "sar"],
    "bandwidth": ["vnstat", "iptraf-ng", "tcptrack", "iftop"],
    "latency": ["ping", "mtr", "tcptrack", "ioping"],
    "ip address": ["ip", "ifconfig", "hostnamectl", "nmcli"],
    "routing": ["ip route", "ip rule", "traceroute", "mtr"],
    "dns": ["dig", "resolvectl", "nslookup", "host"],
    "vpn": ["wg", "openvpn"],
    "wireguard": ["wg", "wg genkey", "wg pubkey", "wg show", "wg showconf"],
    "nfs": ["exportfs", "showmount", "rpcinfo", "mount -t nfs"],
    "samba": ["smbclient", "testparm", "smbstatus", "nmblookup", "pdbedit", "smbpasswd"],
    "file server": ["smbclient", "testparm", "exportfs", "showmount", "mount -t nfs"],
    "who is logged in": ["who", "w", "last", "users", "loginctl"],
    "logged in": ["who", "w", "last", "loginctl", "lastlog"],
    "login history": ["last", "lastlog", "faillog"],
    "user account": ["useradd", "usermod", "userdel", "passwd", "chage", "getent"],
    "password policy": ["chage", "passwd", "pwck", "grpck"],
    "sudo": ["visudo", "sudo -l", "usermod -aG sudo"],
    "running services": ["systemctl", "service", "supervisorctl", "journalctl"],
    "restart service": ["systemctl", "service", "supervisorctl", "nginx", "apache2ctl"],
    "service startup": ["systemd-analyze", "systemctl", "journalctl"],
    "scheduler": ["crontab", "systemctl list-timers", "at"],
    "cron job": ["crontab", "systemctl list-timers", "at"],
    "scheduled task": ["crontab", "systemctl list-timers", "at"],
    "time sync": ["timedatectl", "chronyc", "ntpq", "ntpstat"],
    "ntp": ["chronyc", "ntpq", "ntpstat", "timedatectl"],
    "sessions": ["loginctl", "w", "who", "last"],
    "crash dump": ["coredumpctl", "journalctl"],
    "logs": ["journalctl", "tail", "lnav", "multitail", "dmesg", "logwatch"],
    "check logs": ["journalctl", "tail", "lnav", "multitail", "dmesg"],
    "mail queue": ["mailq", "postqueue", "postsuper", "postfix"],
    "mail server": ["postfix", "mailq", "postqueue", "postconf", "pflogsumm"],
    "ssl certificate": ["certbot", "openssl"],
    "lets encrypt": ["certbot", "openssl"],
    "tls": ["openssl", "certbot"],
    "web server": ["nginx", "apache2ctl", "php-fpm", "certbot"],
    "nginx": ["nginx", "certbot", "journalctl"],
    "apache": ["apache2ctl", "a2ensite", "a2dissite", "a2enmod", "certbot"],
    "php": ["php-fpm", "nginx", "apache2ctl"],
    "backup": ["rsync", "restic", "duplicity", "ddrescue", "testdisk"],
    "restore backup": ["restic restore", "duplicity", "ddrescue", "testdisk"],
    "database backup": ["pg_basebackup", "mongodump", "restic", "mysqldump"],
    "redis": ["redis-cli"],
    "postgres": ["pg_basebackup", "pg_lsclusters", "psql"],
    "mongo": ["mongodump", "mongorestore", "mongosh"],
    "security audit": ["lynis", "rkhunter", "chkrootkit", "auditctl", "ausearch", "aureport"],
    "selinux": ["getenforce", "setenforce", "sestatus", "semanage", "restorecon", "chcon"],
    "apparmor": ["aa-status", "aa-enforce"],
    "capabilities": ["getcap", "setcap"],
    "namespaces": ["unshare", "nsenter"],
    "automation": ["ansible", "terraform", "puppet"],
    "infra as code": ["terraform", "ansible", "puppet"],
    "container": ["docker", "podman", "buildah", "skopeo", "kubectl", "lxc"],
    "kubernetes": ["kubectl", "helm"],
    "virtual machine": ["virsh", "virt-install", "qemu-img"],
    "vm": ["virsh", "virt-install", "qemu-img"],
    "ssh key": ["ssh-keygen", "ssh-copy-id", "ssh"],
    "kill process": ["kill", "pkill", "pgrep", "fuser", "systemctl"],
    "server uptime": ["uptime", "w", "who", "last"],
}


def load_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text())


def merge_synonyms(existing: dict[str, list[str]], additions: dict[str, list[str]]) -> dict[str, list[str]]:
    merged: dict[str, list[str]] = {}
    for source in (existing, additions):
        for key, values in source.items():
            normalized_key = key.strip().lower()
            bucket = merged.setdefault(normalized_key, [])
            for value in values:
                if value not in bucket:
                    bucket.append(value)
    return dict(sorted(merged.items()))


def load_existing_synonyms() -> dict[str, list[str]]:
    if not SEARCH_INDEX_PATH.exists():
        return {}

    try:
        data = load_json(SEARCH_INDEX_PATH)
        synonyms = data.get("synonyms", {})
        if isinstance(synonyms, dict):
            return {
                str(key).strip().lower(): [str(value) for value in values]
                for key, values in synonyms.items()
            }
    except (json.JSONDecodeError, OSError):
        pass
    return {}


def fix_known_data_issue(commands: list[dict[str, object]]) -> bool:
    for command in commands:
        if command.get("id") == 1024:
            if command.get("category") != "User & Group Management":
                command["category"] = "User & Group Management"
                return True
            return False
    return False


def add_missing_commands(data: dict[str, object]) -> list[dict[str, object]]:
    commands = data["commands"]
    assert isinstance(commands, list)

    existing_cmds = {str(command["cmd"]).strip().lower() for command in commands}
    next_id = max(int(command["id"]) for command in commands) + 1
    added: list[dict[str, object]] = []

    for command in EXTRA_COMMANDS:
        normalized = str(command["cmd"]).strip().lower()
        if normalized in existing_cmds:
            continue

        new_command = dict(command)
        new_command["id"] = next_id
        next_id += 1
        commands.append(new_command)
        added.append(new_command)
        existing_cmds.add(normalized)

    commands.sort(key=lambda item: int(item["id"]))
    data["total"] = len(commands)
    return added


def build_tfidf_index(commands: list[dict[str, object]]) -> tuple[dict[str, float], dict[str, dict[str, object]]]:
    doc_freq: Counter[str] = Counter()
    token_counts: dict[int, Counter[str]] = {}

    for command in commands:
        text = " ".join(
            [
                str(command["cmd"]),
                str(command["cmd"]),
                str(command["desc"]),
                str(command["desc"]),
                str(command["category"]),
                str(command.get("tooltip", "")),
            ]
        )
        counts = Counter(tokenize(text))
        token_counts[int(command["id"])] = counts
        for token in counts:
            doc_freq[token] += 1

    total_docs = len(commands)
    idf = {
        token: round(math.log((1 + total_docs) / (1 + freq)) + 1, 6)
        for token, freq in sorted(doc_freq.items())
    }

    index: dict[str, dict[str, object]] = {}
    for command in commands:
        command_id = int(command["id"])
        counts = token_counts[command_id]
        token_total = sum(counts.values()) or 1
        weights = {
            token: round((count / token_total) * idf[token], 6)
            for token, count in sorted(counts.items())
        }
        index[str(command_id)] = {"id": command_id, "tokens": weights}

    return idf, index


def write_json(path: Path, payload: dict[str, object]) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, separators=(",", ":")))


def main() -> None:
    data = load_json(COMMANDS_PATH)
    commands = data["commands"]
    assert isinstance(commands, list)

    fixed = fix_known_data_issue(commands)
    added = add_missing_commands(data)
    synonyms = merge_synonyms(load_existing_synonyms(), SEARCH_SYNONYMS)
    idf, index = build_tfidf_index(commands)

    write_json(COMMANDS_PATH, data)
    write_json(
        SEARCH_INDEX_PATH,
        {
            "synonyms": synonyms,
            "idf": idf,
            "index": index,
        },
    )

    print(
        f"fixed_w_category={fixed} added_commands={len(added)} "
        f"total_commands={data['total']} synonym_keys={len(synonyms)}"
    )


if __name__ == "__main__":
    main()
