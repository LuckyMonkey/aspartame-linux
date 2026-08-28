iso_name="aspartame"
iso_label="ASPARTAME_$(date +%Y%m)"
iso_publisher="Aspartame Linux <aspartame@example.invalid>"
iso_application="Aspartame Linux live environment"
iso_version="$(date +%Y.%m.%d)"
install_dir="arch"
buildmodes=('iso')
bootmodes=('bios.syslinux' 'uefi-x64.systemd-boot')
arch=('x86_64')
airootfs_image_type="squashfs"
file_permissions=(
  ["/etc/shadow"]="0:0:400"
  ["/root/customize_airootfs.sh"]="0:0:755"
)

