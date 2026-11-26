/* lucas-skill 官网逻辑：hash 路由标签切换 + skills.json 渲染 + 作者名片（数据源 yjmm10.github.io，内置快照兜底） */
(function () {
  "use strict";

  var REPO = "https://github.com/yjmm10/lusca-skill";

  /* ---------- 工具 ---------- */
  function $(sel, root) { return (root || document).querySelector(sel); }
  function el(tag, cls, text) {
    var n = document.createElement(tag);
    if (cls) n.className = cls;
    if (text != null) n.textContent = text;
    return n;
  }
  function esc(str) { return String(str == null ? "" : str); }

  /* ---------- hash 路由：#/、#/skills[?cat=x]、#/about ---------- */
  var VIEWS = ["home", "skills", "about"];
  function currentRoute() {
    var h = location.hash || "#/";
    var m = h.match(/^#\/skills(?:\?cat=([\w-]+))?/);
    if (m) return { view: "skills", cat: m[1] || "all" };
    if (h.indexOf("#/about") === 0) return { view: "about", cat: null };
    return { view: "home", cat: null };
  }
  function applyRoute() {
    var r = currentRoute();
    VIEWS.forEach(function (v) {
      var sec = $("#view-" + v);
      if (sec) sec.hidden = v !== r.view;
    });
    Array.prototype.forEach.call($("#nav").children, function (a) {
      a.classList.toggle("on", a.getAttribute("data-view") === r.view);
    });
    if (r.view === "skills") setFilter(r.cat);
    window.scrollTo(0, 0);
  }
  window.addEventListener("hashchange", applyRoute);

  /* ---------- 数据 ---------- */
  var DATA = null;
  var CAT_VAR = { paper: "cat-paper", writing: "cat-writing", research: "cat-research", dev: "cat-dev", meta: "cat-meta" };

  function fetchJSON(url) {
    return fetch(url).then(function (r) {
      if (!r.ok) throw new Error(r.status);
      return r.json();
    });
  }

  function renderStats() {
    var host = $("#stats");
    host.textContent = "";
    [["total", "个 Skill"], ["categories", "大分类"]].forEach(function (p) {
      var d = el("div", "stat");
      d.appendChild(el("b", null, String(DATA.stats[p[0]])));
      d.appendChild(el("span", null, p[1]));
      host.appendChild(d);
    });
    var third = el("div", "stat");
    third.appendChild(el("b", null, "1"));
    third.appendChild(el("span", null, "个唯一源"));
    host.appendChild(third);
  }

  /* ---------- 首页分类卡片 ---------- */
  function renderCats() {
    var grid = $("#cat-grid");
    grid.textContent = "";
    DATA.categories.forEach(function (c) {
      var a = el("a", "cat-card");
      a.href = "#/skills?cat=" + c.id;
      a.appendChild(el("div", "cat-emoji", c.emoji));
      a.appendChild(el("h3", null, c.name));
      a.appendChild(el("p", null, c.desc));
      var cnt = el("div", "cat-count");
      var b = el("b", null, String(c.count));
      cnt.appendChild(b); cnt.appendChild(document.createTextNode(" 个 skill · 点开查看"));
      a.appendChild(cnt);
      grid.appendChild(a);
    });
  }

  /* ---------- Skills 页 ---------- */
  function setFilter(cat) {
    renderFilter(cat);
    renderGroups(cat);
  }
  function renderFilter(active) {
    var bar = $("#filter-bar");
    bar.textContent = "";
    var all = el("button", "filter-pill" + (active === "all" ? " on" : ""), "全部");
    all.type = "button";
    all.addEventListener("click", function () { location.hash = "#/skills"; });
    bar.appendChild(all);
    DATA.categories.forEach(function (c) {
      if (!c.count) return;
      var b = el("button", "filter-pill" + (active === c.id ? " on" : ""), c.emoji + " " + c.name);
      b.type = "button";
      b.addEventListener("click", function () { location.hash = "#/skills?cat=" + c.id; });
      bar.appendChild(b);
    });
  }
  function renderGroups(active) {
    var host = $("#skill-groups");
    host.textContent = "";
    DATA.categories.forEach(function (c) {
      if (!c.count) return;
      if (active !== "all" && active !== c.id) return;
      var group = el("div", "skill-group");
      var head = el("div", "skill-group-head");
      head.appendChild(el("h2", null, c.emoji + " " + c.name));
      head.appendChild(el("span", "cat-en", c.id));
      var cnt = el("span", "cat-count");
      cnt.appendChild(el("b", null, String(c.count)));
      cnt.appendChild(document.createTextNode(" 个"));
      head.appendChild(cnt);
      group.appendChild(head);

      var grid = el("div", "skill-grid");
      c.skills.forEach(function (s) {
        var card = el("article", "skill-card");
        card.style.setProperty("--cat-color", "var(--" + (CAT_VAR[c.id] || "color-border") + ")");

        var headRow = el("div", "skill-card-head");
        headRow.appendChild(el("span", "skill-name", s.name));
        if (s.version) headRow.appendChild(el("span", "skill-ver", "v" + s.version));
        card.appendChild(headRow);

        var desc = el("p", "skill-desc", esc(s.description));
        desc.title = esc(s.description);
        card.appendChild(desc);

        card.appendChild(el("code", "skill-cmd", s.command));
        grid.appendChild(card);
      });
      group.appendChild(grid);
      host.appendChild(group);
    });
  }

  /* ---------- 关于页信息 ---------- */
  function renderAboutInfo() {
    $("#info-count").textContent = DATA.stats.total + " 个";
    $("#info-generated").textContent = DATA.generated_at;
  }

  /* ---------- 作者名片（交互模式参考 fj-starmap：头像点击切换 / 图标悬停二维码 / 技能胶囊悬停标签墙；
       数据取自 yjmm10.github.io profile.json + projects.json，拉取失败用内置快照兜底，首绘无跳动） ---------- */
  var SNAPSHOT = {
    name: "Lucas",
    handle: "yjmm10",
    role: "独立开发者",
    avatar: "https://yjmm10.github.io/assets/avatar.webp",
    avatar_alt: "https://yjmm10.github.io/assets/avatar-alt.webp",
    website: "https://yjmm10.github.io/",
    slogan: "技术是思考的延伸，而不是目的本身",
    expertise: ["智能文档处理", "生成式 AI 全链开发", "无人机轨迹优化"],
    skills: [
      { category: "智能文档处理", items: ["版面分析", "表格解析", "公式解析", "文字识别", "印章识别", "发票解析", "信息抽取", "文档理解", "文档结构化", "文档 RAG"] },
      { category: "生成式 AI 全链开发", items: ["提示词工程", "模型训练", "推理部署", "Agent 开发"] },
      { category: "无人机轨迹优化", items: ["任务卸载", "资源优化", "多机协同", "强化学习", "多目标优化"] }
    ],
    thoughts: ["小而完整，好过大而全。", "被真正用到，才算做完。", "反复打磨，是一种认真。"],
    links: {
      github: "https://github.com/yjmm10",
      email: "lucas4ai@outlook.com",
      wechat_qr: "https://yjmm10.github.io/assets/wechat-qr.png",
      reward_qr: "https://yjmm10.github.io/assets/reward-qr.png"
    }
  };
  var WIP_SNAPSHOT = [
    { name: "DocVLM · 多模态文档智能解析", status: "in-progress" },
    { name: "fj-starmap · AI 创业政策追踪与洞察", status: "tinkering" },
    { name: "Glean · 跨平台内容全自动分发", status: "polishing" },
    { name: "Academic Skill · 科研效率工具集", status: "brewing" }
  ];
  var STATUS = { "in-progress": "进行中", "tinkering": "折腾中", "polishing": "打磨中", "brewing": "构思中" };

  var ICONS = {
    github: '<svg viewBox="0 0 16 16" fill="currentColor" aria-hidden="true"><path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27s1.36.09 2 .27c1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.01 8.01 0 0 0 16 8c0-4.42-3.58-8-8-8Z"/></svg>',
    mail: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="2.5" y="4.5" width="19" height="15" rx="3"/><path d="m3.5 7.5 8.5 5.5 8.5-5.5"/></svg>',
    wechat: '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M9.3 4C5.3 4 2 6.6 2 9.9c0 1.9 1.1 3.5 2.8 4.6L4 17l2.8-1.4c.8.3 1.7.4 2.5.4h.4a5.4 5.4 0 0 1-.2-1.5c0-2.9 2.7-5.2 6-5.2h.5C14.9 6 12.4 4 9.3 4Zm-2 4.2a.9.9 0 1 1 0-1.8.9.9 0 1 1 0 1.8Zm4.6 0a.9.9 0 1 1 0-1.8.9.9 0 1 1 0 1.8Z"/><path d="M22 14.6c0-2.5-2.5-4.6-5.5-4.6S11 12.1 11 14.6s2.5 4.6 5.5 4.6c.8 0 1.5-.1 2.2-.4l2.3 1.2-.6-2c1-.8 1.6-2 1.6-3.4Zm-7.2-.9a.8.8 0 1 1 0-1.6.8.8 0 1 1 0 1.6Zm3.4 0a.8.8 0 1 1 0-1.6.8.8 0 1 1 0 1.6Z"/></svg>',
    coffee: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M17 9h1.5a2.5 2.5 0 0 1 0 5H17"/><path d="M4 9h13v6a4 4 0 0 1-4 4H8a4 4 0 0 1-4-4V9Z"/><path d="M8 3.5v2M11.5 3.5v2M15 3.5v2"/></svg>'
  };

  function boldText(parent, text) {
    String(text || "").split("**").forEach(function (p, i) {
      if (!p) return;
      parent.appendChild(i % 2 === 1 ? el("strong", null, p) : document.createTextNode(p));
    });
  }

  function avatarEl(d) {
    var urls = [d.avatar];
    if (d.avatar_alt && d.avatar_alt !== d.avatar) urls.push(d.avatar_alt);
    var idx = 0;
    var fig = el("figure", "pf-portrait");
    fig.tabIndex = 0;
    fig.setAttribute("role", "button");
    fig.setAttribute("aria-label", "切换头像");
    var img = new Image();
    img.alt = d.name; img.loading = "lazy"; img.referrerPolicy = "no-referrer";
    function use(i) { idx = i; img.src = urls[i]; }
    img.onerror = function () {
      if (idx + 1 < urls.length) { use(idx + 1); return; }
      img.remove();
      fig.insertBefore(el("span", "pf-ava-letter", (d.name || "L").charAt(0).toUpperCase()), fig.firstChild);
    };
    function toggle() { if (urls.length > 1) use((idx + 1) % urls.length); }
    fig.addEventListener("click", toggle);
    fig.addEventListener("keydown", function (e) {
      if (e.key === "Enter" || e.key === " ") { e.preventDefault(); toggle(); }
    });
    if (urls.length > 1) fig.title = "点击切换头像";
    fig.appendChild(img);
    use(0);
    return fig;
  }

  function socLink(href, svg, label, external) {
    var a = el("a", "pf-soc-btn");
    a.href = href; a.innerHTML = svg; a.title = label;
    a.setAttribute("aria-label", label);
    if (external) { a.target = "_blank"; a.rel = "noopener"; }
    return a;
  }
  function socQR(svg, label, src) {
    var wrap = el("div", "pf-soc");
    wrap.appendChild(socLink("#", svg, label, false));
    var btn = wrap.querySelector("a");
    btn.removeAttribute("href");
    var fig = el("figure", "pf-pop");
    var img = new Image();
    img.src = src; img.alt = label; img.loading = "lazy"; img.referrerPolicy = "no-referrer";
    img.onerror = function () { wrap.remove(); };
    fig.appendChild(img);
    fig.appendChild(el("figcaption", null, label));
    wrap.appendChild(fig);
    return wrap;
  }

  /* 双语字段归一：{en,zh} 对象取中文优先，字符串原样 —— 渲染层只吃纯字符串，避免 [object Object] */
  function pick(o) {
    if (o == null) return "";
    if (typeof o === "string") return o;
    if (typeof o === "object") return o.zh || o.en || "";
    return String(o);
  }

  function normalizeProfile(d) {
    d = d || {};
    var links = d.links || {};
    var skills = Array.isArray(d.skills) && d.skills.length ? d.skills : SNAPSHOT.skills;
    var thoughts = Array.isArray(d.thoughts) && d.thoughts.length ? d.thoughts : SNAPSHOT.thoughts;
    return {
      name: pick(d.name) || SNAPSHOT.name,
      handle: pick(d.handle) || SNAPSHOT.handle,
      role: pick(d.role) || SNAPSHOT.role,
      avatar: d.avatar || SNAPSHOT.avatar,
      avatar_alt: d.avatar_alt || SNAPSHOT.avatar_alt,
      slogan: pick(d.slogan) || SNAPSHOT.slogan,
      skills: skills.map(function (g) {
        return {
          category: pick(g.category),
          items: (Array.isArray(g.items) ? g.items : []).map(pick).filter(Boolean)
        };
      }).filter(function (g) { return g.category && g.items.length; }),
      thoughts: thoughts.map(pick).filter(Boolean),
      links: {
        github: links.github || SNAPSHOT.links.github,
        email: links.email || SNAPSHOT.links.email,
        wechat_qr: links.wechat_qr || SNAPSHOT.links.wechat_qr,
        reward_qr: links.reward_qr || SNAPSHOT.links.reward_qr
      }
    };
  }

  function renderProfile(d, wip) {
    var host = $("#profile");
    host.textContent = "";

    /* 左栏：头像 + 身份 + 社交 + 技能胶囊 */
    var me = el("div", "pf-me");
    me.appendChild(avatarEl(d));

    var nameRow = el("div", "pf-name-row");
    nameRow.appendChild(el("span", "pf-name", d.name));
    var hd = el("a", "pf-handle", "@" + d.handle);
    hd.href = d.links.github; hd.target = "_blank"; hd.rel = "noopener";
    nameRow.appendChild(hd);
    me.appendChild(nameRow);

    me.appendChild(el("div", "pf-role", d.role));

    var social = el("div", "pf-social");
    social.appendChild(socLink(d.links.github, ICONS.github, "GitHub", true));
    social.appendChild(socLink("mailto:" + d.links.email, ICONS.mail, d.links.email, false));
    if (d.links.wechat_qr) social.appendChild(socQR(ICONS.wechat, "微信 · 加个好友", d.links.wechat_qr));
    if (d.links.reward_qr) social.appendChild(socQR(ICONS.coffee, "赞赏 · 请我喝咖啡", d.links.reward_qr));
    me.appendChild(social);

    var slab = el("div", "pf-skill-label", "擅 长 领 域");
    me.appendChild(slab);
    var sk = el("div", "pf-skills");
    d.skills.forEach(function (g) {
      var pop = el("div", "pf-skill-pop");
      var btn = el("button", "pf-skill", g.category);
      btn.type = "button";
      var tip = el("div", "pf-tip");
      g.items.forEach(function (it, i) {
        if (i > 0) tip.appendChild(document.createTextNode(" · "));
        tip.appendChild(el("span", null, it));
      });
      pop.appendChild(btn); pop.appendChild(tip);
      sk.appendChild(pop);
    });
    me.appendChild(sk);
    host.appendChild(me);

    /* 右栏：座右铭 / 在搞的项目 / 个人想法 */
    var right = el("div", "pf-intro");
    var sl = el("p", "pf-slogan");
    sl.appendChild(el("span", "pf-quote", "❝ "));
    sl.appendChild(document.createTextNode(d.slogan));
    sl.appendChild(el("span", "pf-quote", " ❞"));
    right.appendChild(sl);

    var wsec = el("section");
    wsec.appendChild(el("h3", "pf-col-title", "在搞的项目"));
    var wul = el("ul", "pf-list");
    wip.forEach(function (p) {
      var li = el("li");
      li.appendChild(el("span", "pf-dot"));
      li.appendChild(el("span", null, p.name));
      var st = el("em", "pf-st" + (STATUS[p.status] ? " st-" + p.status : ""), STATUS[p.status] || p.status || "");
      li.appendChild(st);
      wul.appendChild(li);
    });
    wsec.appendChild(wul);
    right.appendChild(wsec);

    var tsec = el("section");
    tsec.appendChild(el("h3", "pf-col-title", "个人想法"));
    var tul = el("ul", "pf-list");
    d.thoughts.forEach(function (t) {
      var li = el("li");
      boldText(li, t);
      tul.appendChild(li);
    });
    tsec.appendChild(tul);
    right.appendChild(tsec);

    host.appendChild(right);
  }

  function initProfile() {
    renderProfile(SNAPSHOT, WIP_SNAPSHOT); /* 同步首绘，再异步回填最新数据 */
    Promise.all([
      fetchJSON("https://yjmm10.github.io/profile.json").catch(function () { return SNAPSHOT; }),
      fetchJSON("https://yjmm10.github.io/projects.json")
        .then(function (d) {
          return (d && Array.isArray(d.wip)) ? d.wip.map(function (p) {
            var name = pick(p.name);
            var tag = pick(p.tagline);
            return {
              name: tag ? name + " · " + tag : name,
              status: p.status || ""
            };
          }) : WIP_SNAPSHOT;
        })
        .catch(function () { return WIP_SNAPSHOT; })
    ]).then(function (r) {
      try { renderProfile(normalizeProfile(r[0]), r[1]); } catch (e) { /* 回填失败保留首绘 */ }
    });
  }

  /* ---------- 启动 ---------- */
  fetchJSON("data/skills.json").then(function (data) {
    DATA = data;
    renderStats();
    renderCats();
    renderAboutInfo();
    initProfile();
    applyRoute();
  }).catch(function () {
    $("#stats").textContent = "";
    var warn = el("p", null, "站点数据加载失败（data/skills.json）——请在仓库根重跑 python scripts/build-site-data.py。");
    warn.style.color = "var(--color-danger)";
    $("#cat-grid").appendChild(warn);
    applyRoute();
  });
})();
