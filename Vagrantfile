# Headless Debian 12 VM that runs the phishing prevention proxy on boot.
#
#   vagrant up        build/boot the VM (first run downloads the box + model)
#   vagrant provision re-copy the code and restart the proxy after changes
#   vagrant halt      shut it down
#   vagrant destroy   delete it
#
# Point the browser's HTTP proxy at 192.168.56.10:8080 (or 127.0.0.1:8080).

Vagrant.configure("2") do |config|
  config.vm.box = "bento/debian-12"
  config.vm.hostname = "phishing-proxy"

  # Fixed host-only IP so the demo always uses the same proxy address
  config.vm.network "private_network", ip: "192.168.56.10"

  # Fallback: also reachable on the host's localhost
  config.vm.network "forwarded_port", guest: 8080, host: 8080, host_ip: "127.0.0.1"

  config.vm.provider "virtualbox" do |vb|
    vb.name = "phishing-proxy"
    vb.memory = 1024
    vb.cpus = 1
  end

  # The repo is shared at /vagrant; provision.sh copies it to /opt/proxy
  config.vm.provision "shell", path: "provision.sh"
end
