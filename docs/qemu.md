# QEMU reference machine

```sh
make iso
RAM=4096 CPUS=4 make run
```

The runner uses KVM and `-cpu host` when `/dev/kvm` is accessible, otherwise it
falls back to TCG. It provides a q35 machine, virtio disk/network, virtio VGA,
USB tablet, PulseAudio/PipeWire-backed AC97 audio, and a separate persistent
qcow2 test disk at `runtime/`.
