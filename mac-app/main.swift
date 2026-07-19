import Cocoa
import WebKit

// 数据来源：本地稳定路径 + Worker 远程源（管线迁到 Studio 后由远程更新本地副本）
let APP_DIR = ("~/Library/Application Support/ZoeTime" as NSString).expandingTildeInPath
let HTML_PATH = APP_DIR + "/index.html"
let REMOTE_URL = "https://zoe-time-sync.zoe-mt.workers.dev/html"
let ZT_TOKEN = "41326c953ec9ceb6227a27adc2cc83e583b9db05454e77f0"

class AppDelegate: NSObject, NSApplicationDelegate, WKNavigationDelegate {
    var window: NSWindow!
    var web: WKWebView!
    var lastMtime: Date?

    func applicationDidFinishLaunching(_ note: Notification) {
        let cfg = WKWebViewConfiguration()
        cfg.websiteDataStore = .default()               // 持久化 localStorage（补录/纠错/目标存本机）
        let rect = NSRect(x: 0, y: 0, width: 460, height: 940)
        web = WKWebView(frame: rect, configuration: cfg)
        web.navigationDelegate = self

        window = NSWindow(contentRect: rect,
                          styleMask: [.titled, .closable, .miniaturizable, .resizable],
                          backing: .buffered, defer: false)
        window.title = "Zoe · 时间"
        window.minSize = NSSize(width: 380, height: 560)
        window.center()
        window.contentView = web
        window.makeKeyAndOrderFront(nil)
        window.isReleasedWhenClosed = false

        loadHTML()
        fetchRemote()                                    // 启动就拉一次远程最新
        Timer.scheduledTimer(withTimeInterval: 1800, repeats: true) { _ in self.fetchRemote() }  // 常开每30分钟
        NSApp.activate(ignoringOtherApps: true)
    }

    // 从 Worker 拉最新页面：有更新 → 覆写本地副本并热替换；失败静默（本地照常，离线可用）
    func fetchRemote() {
        guard var req = URL(string: REMOTE_URL).map({ URLRequest(url: $0) }) else { return }
        req.setValue(ZT_TOKEN, forHTTPHeaderField: "X-ZT-Token")
        req.timeoutInterval = 30
        URLSession.shared.dataTask(with: req) { data, resp, _ in
            guard let d = data, d.count > 50_000,
                  (resp as? HTTPURLResponse)?.statusCode == 200 else { return }
            let old = FileManager.default.contents(atPath: HTML_PATH)
            if old == d { return }                       // 没变不折腾
            try? FileManager.default.createDirectory(atPath: APP_DIR, withIntermediateDirectories: true)
            guard (try? d.write(to: URL(fileURLWithPath: HTML_PATH))) != nil else { return }
            DispatchQueue.main.async { self.loadHTML() } // 热替换到最新
        }.resume()
    }

    func loadHTML() {
        let fm = FileManager.default
        guard fm.fileExists(atPath: HTML_PATH) else {
            web.loadHTMLString("<div style='font-family:-apple-system;padding:40px;color:#555'>数据还在生成中…<br>请稍后打开，或在终端跑一次 refresh.py。</div>", baseURL: nil)
            return
        }
        lastMtime = (try? fm.attributesOfItem(atPath: HTML_PATH)[.modificationDate]) as? Date
        let url = URL(fileURLWithPath: HTML_PATH)
        web.loadFileURL(url, allowingReadAccessTo: URL(fileURLWithPath: APP_DIR))
    }

    // 每次切回 App：仅当底层文件更新了才重载（拿到最新数据，又不打断正在看的视图）
    func applicationDidBecomeActive(_ note: Notification) {
        guard web != nil else { return }
        let m = (try? FileManager.default.attributesOfItem(atPath: HTML_PATH)[.modificationDate]) as? Date
        if let m = m, m != lastMtime { loadHTML() }
        fetchRemote()                                    // 切回前台也拉一次
    }

    @objc func reloadNow() { loadHTML() }
    func applicationShouldTerminateAfterLastWindowClosed(_ s: NSApplication) -> Bool { return true }
}

let app = NSApplication.shared
app.setActivationPolicy(.regular)
let delegate = AppDelegate()
app.delegate = delegate

// 菜单：Cmd+R 刷新数据 / Cmd+Q 退出（复制粘贴等标准编辑）
let mainMenu = NSMenu()
let appItem = NSMenuItem(); mainMenu.addItem(appItem)
let appMenu = NSMenu()
let r = appMenu.addItem(withTitle: "刷新数据", action: #selector(AppDelegate.reloadNow), keyEquivalent: "r"); r.target = delegate
appMenu.addItem(NSMenuItem.separator())
appMenu.addItem(withTitle: "隐藏", action: #selector(NSApplication.hide(_:)), keyEquivalent: "h")
appMenu.addItem(withTitle: "退出 Zoe · 时间", action: #selector(NSApplication.terminate(_:)), keyEquivalent: "q")
appItem.submenu = appMenu
let editItem = NSMenuItem(); mainMenu.addItem(editItem)
let editMenu = NSMenu(title: "编辑")
editMenu.addItem(withTitle: "拷贝", action: #selector(NSText.copy(_:)), keyEquivalent: "c")
editMenu.addItem(withTitle: "粘贴", action: #selector(NSText.paste(_:)), keyEquivalent: "v")
editMenu.addItem(withTitle: "全选", action: #selector(NSText.selectAll(_:)), keyEquivalent: "a")
editItem.submenu = editMenu
app.mainMenu = mainMenu

app.run()
