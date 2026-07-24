(function (window, document) {
  "use strict";
  if (window.__vidcoChatWidgetLoaded) return;
  window.__vidcoChatWidgetLoaded = true;

  var DEFAULT_CHAT_HOST = "https://chat.vidco.com.tr";
  var READY_TIMEOUT_MS = 10000;
  var SESSION_TIMEOUT_MS = 15000;

  function resolveChatHost() {
    var currentScript = document.currentScript;
    if (currentScript && currentScript.src) {
      try {
        return new URL(currentScript.src).origin;
      } catch (error) {}
    }
    return DEFAULT_CHAT_HOST;
  }

  var CHAT_HOST = resolveChatHost();

  var widgetState = {
    initialized: false,
    booting: false,
    ready: false,
    iframe: null,
    container: null,
    config: null,
    pendingMessages: [],
    lifecycleId: 0,
    sessionController: null
  };

  function normalizeRoles(roles) {
    if (Array.isArray(roles)) return roles.map(function (role) { return String(role).trim(); }).filter(Boolean);
    if (typeof roles === "string") return roles.split(";").map(function (role) { return role.trim(); }).filter(Boolean);
    return [];
  }

  function getCurrentPage() {
    return window.location.origin + window.location.pathname;
  }

  function normalizeConfig(config) {
    if (!config || !config.botId) throw new Error("VidcoChat: botId zorunludur.");

    return {
      botId: config.botId,
      user: {
        username: (config.user && config.user.username) || null,
        userEmail: (config.user && config.user.userEmail) || null,
        userRoles: normalizeRoles(config.user && config.user.userRoles)
      },
      context: {
        currentPage: (config.context && config.context.currentPage) || getCurrentPage(),
        pageTitle: (config.context && config.context.pageTitle) || document.title
      },
      identityToken: config.identityToken || null
    };
  }

  function createSession(config, controller) {
    var timeoutId = window.setTimeout(function () { controller.abort(); }, SESSION_TIMEOUT_MS);

    return fetch(CHAT_HOST + "/api/widget/session", {
      method: "POST",
      signal: controller.signal,
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        botId: config.botId,
        user: config.user,
        context: config.context,
        identityToken: config.identityToken,
        origin: window.location.origin
      })
    })
      .then(function (response) {
        if (!response.ok) throw new Error("Chatbot oturumu oluşturulamadı.");
        return response.json();
      })
      .finally(function () { window.clearTimeout(timeoutId); });
  }

  function isValidSessionResponse(session) {
    return !!(session && typeof session.sessionToken === "string" && session.sessionToken.trim().length > 0);
  }

  function appendContainer(container) {
    if (document.body) {
      document.body.appendChild(container);
      return;
    }

    document.addEventListener(
      "DOMContentLoaded",
      function () {
        if (widgetState.container === container && document.body) document.body.appendChild(container);
      },
      { once: true }
    );
  }

  function createWidget(sessionToken) {
    if (widgetState.container) return;

    var container = document.createElement("div");
    container.id = "vidco-chat-container";
    Object.assign(container.style, {
      position: "fixed",
      right: "20px",
      bottom: "20px",
      width: "80px",
      height: "80px",
      zIndex: "2147483647"
    });

    var iframe = document.createElement("iframe");
    iframe.id = "vidco-chat-iframe";
    iframe.title = "Vidco Chatbot";
    iframe.src = CHAT_HOST + "/embed?session=" + encodeURIComponent(sessionToken);
    iframe.setAttribute("allow", "microphone; clipboard-write");
    Object.assign(iframe.style, { width: "100%", height: "100%", border: "none", background: "transparent" });

    container.appendChild(iframe);
    appendContainer(container);

    widgetState.container = container;
    widgetState.iframe = iframe;
    widgetState.initialized = true;

    window.setTimeout(function () {
      if (widgetState.iframe === iframe && !widgetState.ready) {
        console.error("VidcoChat: Iframe belirtilen sürede (" + READY_TIMEOUT_MS + "ms) hazır olmadı.");
      }
    }, READY_TIMEOUT_MS);
  }

  function boot(config) {
    if (widgetState.booting || widgetState.initialized) {
      console.warn("VidcoChat: boot zaten çalıştırıldı, tekrar çağrı yok sayıldı.");
      return;
    }

    var normalizedConfig;
    try {
      normalizedConfig = normalizeConfig(config);
    } catch (error) {
      console.error("VidcoChat:", error);
      return;
    }

    widgetState.booting = true;
    widgetState.config = normalizedConfig;

    var lifecycleId = ++widgetState.lifecycleId;
    var controller = new AbortController();
    widgetState.sessionController = controller;

    createSession(normalizedConfig, controller)
      .then(function (session) {
        if (lifecycleId !== widgetState.lifecycleId) return;

        widgetState.sessionController = null;
        widgetState.booting = false;

        if (!isValidSessionResponse(session)) {
          console.error("VidcoChat: Sunucudan geçersiz oturum yanıtı geldi.");
          return;
        }

        createWidget(session.sessionToken);
      })
      .catch(function (error) {
        if (lifecycleId !== widgetState.lifecycleId) return;

        widgetState.sessionController = null;
        widgetState.booting = false;

        if (error && error.name === "AbortError") {
          console.error("VidcoChat: Oturum isteği zaman aşımına uğradı veya iptal edildi.");
          return;
        }

        console.error("VidcoChat:", error);
      });
  }

  function sendToIframe(type, payload) {
    var message = { source: "vidco-chat-parent", type: type, payload: payload || {} };

    if (!widgetState.ready || !widgetState.iframe || !widgetState.iframe.contentWindow) {
      widgetState.pendingMessages.push(message);
      return;
    }

    widgetState.iframe.contentWindow.postMessage(message, CHAT_HOST);
  }

  function flushPendingMessages() {
    if (!widgetState.iframe || !widgetState.iframe.contentWindow) return;

    widgetState.pendingMessages.forEach(function (message) {
      widgetState.iframe.contentWindow.postMessage(message, CHAT_HOST);
    });

    widgetState.pendingMessages = [];
  }

  function clamp(value, min, max) {
    return Math.min(Math.max(value, min), max);
  }

  function handleIframeResize(payload) {
    if (!widgetState.container || !payload) return;

    var maxWidth = Math.max(60, Math.min(560, window.innerWidth - 20));
    var maxHeight = Math.max(60, Math.min(820, window.innerHeight - 20));

    if (typeof payload.width === "number" && Number.isFinite(payload.width)) widgetState.container.style.width = clamp(payload.width, 60, maxWidth) + "px";
    if (typeof payload.height === "number" && Number.isFinite(payload.height)) widgetState.container.style.height = clamp(payload.height, 60, maxHeight) + "px";

    var isOpenPanel = typeof payload.height === "number" && payload.height > 100;
    Object.assign(widgetState.container.style, {
      borderRadius: isOpenPanel ? "20px" : "0",
      boxShadow: isOpenPanel ? "0 16px 56px rgba(35, 20, 40, 0.22), 0 2px 8px rgba(35, 20, 40, 0.08)" : "none",
      overflow: isOpenPanel ? "hidden" : "visible"
    });
  }

  function handleParentMessage(event) {
    if (event.origin !== CHAT_HOST) return;
    if (!widgetState.iframe || event.source !== widgetState.iframe.contentWindow) return;

    var data = event.data;
    if (!data || data.source !== "vidco-chat-iframe") return;

    switch (data.type) {
      case "READY":
        widgetState.ready = true;
        flushPendingMessages();
        break;

      case "RESIZE":
        handleIframeResize(data.payload);
        break;

      default:
        break;
    }
  }

  window.addEventListener("message", handleParentMessage);

  function open() { sendToIframe("OPEN"); }
  function close() { sendToIframe("CLOSE"); }

  function updateUser(user) {
    var normalizedUser = {
      username: (user && user.username) || null,
      userEmail: (user && user.userEmail) || null,
      userRoles: normalizeRoles(user && user.userRoles)
    };

    if (widgetState.config) widgetState.config.user = normalizedUser;
    sendToIframe("UPDATE_USER", normalizedUser);
  }

  function updateContext(context) {
    var normalizedContext = {
      currentPage: (context && context.currentPage) || getCurrentPage(),
      pageTitle: (context && context.pageTitle) || document.title
    };

    if (widgetState.config) widgetState.config.context = normalizedContext;
    sendToIframe("UPDATE_CONTEXT", normalizedContext);
  }

  function shutdown() {
    widgetState.lifecycleId += 1;
    if (widgetState.sessionController) widgetState.sessionController.abort();
    if (widgetState.container) widgetState.container.remove();

    widgetState.initialized = false;
    widgetState.booting = false;
    widgetState.ready = false;
    widgetState.iframe = null;
    widgetState.container = null;
    widgetState.config = null;
    widgetState.pendingMessages = [];
    widgetState.sessionController = null;
  }

  function executeCommand(command, payload) {
    switch (command) {
      case "boot": boot(payload); break;
      case "open": open(); break;
      case "close": close(); break;
      case "updateUser": updateUser(payload); break;
      case "updateContext": updateContext(payload); break;
      case "shutdown": shutdown(); break;
      default: console.warn("VidcoChat: Geçersiz komut:", command);
    }
  }

  function queueContainsBoot(commands) {
    return commands.some(function (args) { return args[0] === "boot"; });
  }

  var queuedCommands = (window.VidcoChat && window.VidcoChat.q) || [];

  window.VidcoChat = function (command, payload) { executeCommand(command, payload); };

  if (!queueContainsBoot(queuedCommands) && window.VidcoChatConfig) boot(window.VidcoChatConfig);

  queuedCommands.forEach(function (args) { executeCommand(args[0], args[1]); });
})(window, document);