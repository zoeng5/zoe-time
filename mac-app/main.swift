import Cocoa
import WebKit

// 数据来源：稳定路径（refresh.py 每次刷新会同步过来，抗目录迁移）
let APP_DIR = ("~/Library/Application Support/ZoeTime" as NSString).expandingTildeInPath
let HTML_PATH = APP_DIR + "/index.html"

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
        NSApp.activate(ignoringOtherApps: true)
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
