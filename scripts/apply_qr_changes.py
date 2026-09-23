"""Apply Phase 3.6.x QR-code top-up changes to index.html.
   Reads, edits in-memory, writes back via UTF-8 (avoids PowerShell
   em-dash corruption)."""
from pathlib import Path
import re

p = Path(r'C:\Users\Administrator\protocol-scout\index.html')
text = p.read_text(encoding='utf-8')

# 1. Add CDN script tag before the main app <script> block.
needle = '<script>\n\n  const API_URL ='
replacement = (
    '<!-- QR generator for top-up modal (loaded from jsdelivr CDN). -->\n'
    '<script src="https://cdn.jsdelivr.net/npm/qrcode-generator@1.4.4/qrcode.min.js" '
    'crossorigin="anonymous"></script>\n\n'
    '<script>\n\n  const API_URL ='
)
if needle not in text:
    raise SystemExit('Anchor for CDN script not found')
text = text.replace(needle, replacement, 1)

# 2. Replace the "Send USDC to this address" block with one that shows
#    a QR code next to the receiver address.
old_block = '''<div class="topup-block">
      <div style="font-size:13px;color:#888;margin-bottom:8px;">2. Send USDC to this address</div>
      <div id="topupReceiver" class="topup-receiver">\u2014</div>
      <div style="margin-top:8px;font-size:12px;color:#888;">
        Network: <span id="topupNetworkName">\u2014</span>
      </div>
    </div>'''
new_block = '''<div class="topup-block">
      <div style="font-size:13px;color:#888;margin-bottom:8px;">2. Send USDC to this address</div>
      <div style="display:flex;gap:14px;align-items:flex-start;flex-wrap:wrap;">
        <div id="topupQrWrap" style="flex:0 0 auto;background:#fff;padding:8px;border-radius:6px;border:1px solid #333;">
          <div id="topupQr" style="width:160px;height:160px;display:flex;align-items:center;justify-content:center;color:#888;font-size:11px;">Loading\u2026</div>
        </div>
        <div style="flex:1;min-width:200px;">
          <div id="topupReceiver" class="topup-receiver">\u2014</div>
          <div style="margin-top:8px;font-size:12px;color:#888;">
            Network: <span id="topupNetworkName">\u2014</span>
          </div>
          <div style="margin-top:8px;font-size:11px;color:#666;">
            Scan with a Web3 wallet (MetaMask, Rabby, Coinbase, etc.) to prefill the transfer.
          </div>
        </div>
      </div>
    </div>'''
if old_block not in text:
    raise SystemExit('topup block anchor not found')
text = text.replace(old_block, new_block, 1)

# 3. Update topupState to include chainId + usdcTokenAddress.
old_state = '''  const topupState = {
    receiverAddress: null,
    chainName: null,
    creditsPerUsdc: 10,
    selectedUsdc: 5,'''
new_state = '''  const topupState = {
    receiverAddress: null,
    chainName: null,
    chainId: null,
    usdcTokenAddress: null,
    creditsPerUsdc: 10,
    selectedUsdc: 5,'''
if old_state not in text:
    raise SystemExit('topupState anchor not found')
text = text.replace(old_state, new_state, 1)

# 4. Save chainId + usdcTokenAddress in loadBillingInfo.
old_load = '''      topupState.receiverAddress = data.receiverAddress || null;
      topupState.chainName =
        data.network?.chainName || "Base";
      topupState.creditsPerUsdc =
        data.pricing?.creditsPerUsdc || 10;'''
new_load = '''      topupState.receiverAddress = data.receiverAddress || null;
      topupState.chainName =
        data.network?.chainName || "Base";
      topupState.chainId =
        data.network?.chainId || null;
      // Pick USDC for the QR \u2014 multi-token support later if needed.
      const tokensArr = data.tokens || (data.token ? [data.token] : []);
      const usdcToken = tokensArr.find(
        (t) => String(t.symbol || "").toUpperCase() === "USDC"
      );
      topupState.usdcTokenAddress =
        (usdcToken && usdcToken.address) || null;
      topupState.creditsPerUsdc =
        data.pricing?.creditsPerUsdc || 10;'''
if old_load not in text:
    raise SystemExit('loadBillingInfo anchor not found')
text = text.replace(old_load, new_load, 1)

# 5. Add QR rendering functions after updateTopupCreditsLabel.
old_credits = '''  function updateTopupCreditsLabel() {
    const credits = topupState.selectedUsdc * topupState.creditsPerUsdc;
    topupCreditsLabel.textContent =
      "= " + credits + " credits";
  }'''
new_credits = old_credits + '''

  // EIP-681 URI so wallets prefill the transfer when they scan.
  //   ethereum:<TOKEN>@<CHAIN_ID>/transfer?address=<RECEIVER>&uint256=<AMOUNT_RAW>
  // USDC has 6 decimals, so 5 USDC = 5_000_000.
  function buildTopupUri() {
    const {
      receiverAddress, usdcTokenAddress, chainId, selectedUsdc,
    } = topupState;
    if (!receiverAddress || !usdcTokenAddress || !chainId) return null;
    const amountRaw = BigInt(Math.floor(selectedUsdc * 1_000_000)).toString();
    return (
      "ethereum:" + usdcTokenAddress +
      "@" + chainId +
      "/transfer?address=" + receiverAddress +
      "&uint256=" + amountRaw
    );
  }

  function renderTopupQr() {
    const el = document.getElementById("topupQr");
    if (!el) return;
    const uri = buildTopupUri();
    if (!uri) {
      el.innerHTML =
        '<span style="color:#666;font-size:11px;">Unavailable</span>';
      return;
    }
    if (typeof qrcode !== "function") {
      el.innerHTML =
        '<span style="color:#666;font-size:10px;word-break:break-all;padding:6px;">' +
        escapeHtml(uri) + "</span>";
      return;
    }
    try {
      // Type 4 ~ 33x33 modules is plenty for a short EIP-681 URI on a
      // 160px canvas (each module ~4px). Error correction "M" is fine \u2014
      // wallets usually scan in good light.
      const qr = qrcode(4, "M");
      qr.addData(uri);
      qr.make();
      el.innerHTML = qr.createSvgTag({
        cellSize: 4,
        margin: 2,
        scalable: true,
        alt: "Top-up " + topupState.selectedUsdc + " USDC to " +
             topupState.receiverAddress,
      });
    } catch (e) {
      el.textContent = "QR error: " + (e.message || e);
    }
  }'''
if old_credits not in text:
    raise SystemExit('updateTopupCreditsLabel anchor not found')
text = text.replace(old_credits, new_credits, 1)

# 6. Call renderTopupQr at end of openTopup.
old_open = '''    topupTxHash.value = "";
    await loadBillingInfo();
    updateTopupCreditsLabel();
  }'''
new_open = '''    topupTxHash.value = "";
    await loadBillingInfo();
    updateTopupCreditsLabel();
    renderTopupQr();
  }'''
if old_open not in text:
    raise SystemExit('openTopup tail anchor not found')
text = text.replace(old_open, new_open, 1)

# 7. Call renderTopupQr in amount click handler.
old_click = '''    updateTopupCreditsLabel();
  });'''
new_click = '''    updateTopupCreditsLabel();
    renderTopupQr();
  });'''
if old_click not in text:
    raise SystemExit('amount click anchor not found')
text = text.replace(old_click, new_click, 1)

p.write_text(text, encoding='utf-8')
print('All 7 changes applied.')