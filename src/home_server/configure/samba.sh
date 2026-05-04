#! /usr/bin/env bash

# Copyright (c) 2026 sharm294
# SPDX-License-Identifier: AGPL-3.0-or-later

SAMBA_USER="nas_admin"
SAMBA_GROUP="nas_users"
SAMBA_PASSWORD="changeme"

groupadd -g "10000" "$SAMBA_GROUP" 2>/dev/null
useradd -u "1000" -s /usr/sbin/nologin -M -G "$SAMBA_GROUP" "$SAMBA_USER" 2>/dev/null

apt-get update
apt-get install -y samba acl

printf '%s\n%s\n' "$SAMBA_PASSWORD" "$SAMBA_PASSWORD" | smbpasswd -s -a "$SAMBA_USER"

# Create share directories with correct ownership
for dir in /mnt/nas /mnt/media_root; do
  mkdir -p "$dir"
  chown "${SAMBA_USER}:${SAMBA_USER}" "$dir"
  chmod 0775 "$dir"
done

# Write smb.conf
cat > /etc/samba/smb.conf << 'EOF'
[global]
   workgroup = WORKGROUP
   server string = Samba Server
   server role = standalone server
   log file = /var/log/samba/log.%m
   max log size = 50
   dns proxy = no
   map to guest = never
   min protocol = SMB2

   # macOS compatibility (fruit VFS)
   vfs objects = fruit streams_xattr
   fruit:metadata = stream
   fruit:model = MacSamba
   fruit:posix_rename = yes
   fruit:veto_appledouble = no
   fruit:nfs_aces = no
   fruit:wipe_intentionally_left_blank_rfork = yes
   fruit:delete_empty_adfiles = yes

[nas]
   path = /mnt/nas
   comment = NAS Share
   read only = no
   browseable = yes
   valid users = nas_admin
   force user = nas_admin
   force group = nas_users
   create mask = 0664
   directory mask = 0775

[media]
   path = /mnt/media_root
   comment = Media Share
   read only = no
   browseable = yes
   valid users = nas_admin
   force user = nas_admin
   force group = nas_users
   create mask = 0664
   directory mask = 0775
EOF

# Enable and start samba
systemctl enable smbd
systemctl start smbd

echo "Samba is configured and running."
