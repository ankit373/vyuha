class Vyuha < Formula
  desc "Elite high-governance multi-agent engine"
  homepage "https://github.com/your-username/vyuha"
  url "https://github.com/your-username/vyuha/archive/refs/tags/v0.1.0.tar.gz"
  sha256 "REPLACE_WITH_ACTUAL_SHA256"
  license "MIT"

  depends_on "python@3.12"

  def install
    virtualenv_install_with_resources
  end

  test do
    system "#{bin}/vyuha", "--help"
  end
end
