#!/bin/bash
set -e
iptables -N JFRED-PRIVATE 2>/dev/null || true
iptables -F JFRED-PRIVATE
iptables -A JFRED-PRIVATE -m conntrack --ctstate ESTABLISHED,RELATED -j RETURN
iptables -A JFRED-PRIVATE -s 192.168.0.0/24 -j RETURN
iptables -A JFRED-PRIVATE -s 10.144.144.0/24 -j RETURN
iptables -A JFRED-PRIVATE -s 127.0.0.0/8 -j RETURN
iptables -A JFRED-PRIVATE -j DROP
for port in 18081 18082 18083 18084 18086; do
 iptables -C DOCKER-USER -p tcp -m conntrack --ctorigdstport "$port" -j JFRED-PRIVATE 2>/dev/null || iptables -I DOCKER-USER 1 -p tcp -m conntrack --ctorigdstport "$port" -j JFRED-PRIVATE
done
