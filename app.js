// ===========================
//  BeamAdmin — app.js
// ===========================

// Authentication is handled by the BeamAdmin API.

const MAX_ATTEMPTS = 5;
let attempts = 0;

// -------------------------------------------------
//  Element refs
// -------------------------------------------------
const loginScreen   = document.getElementById('login-screen');
const dashboard     = document.getElementById('dashboard');
const loginBtn      = document.getElementById('login-btn');
const errMsg        = document.getElementById('err-msg');
const attemptsTxt   = document.getElementById('attempts-txt');
const usernameInput = document.getElementById('username');
const pwInput       = document.getElementById('password');
const pwToggle      = document.getElementById('pw-toggle');
const eyeIcon       = document.getElementById('eye-icon');
const logoutBtn     = document.getElementById('logout-btn');
const loggedInUser  = document.getElementById('logged-in-user');
const pageTitle     = document.getElementById('page-title');

// -------------------------------------------------
//  Login
// -------------------------------------------------
async function doLogin() {
  if (attempts >= MAX_ATTEMPTS) return;

  const user = usernameInput.value.trim();
  const pass = pwInput.value;

  loginBtn.disabled = true;
  errMsg.textContent = '';

  const loginOk = await apiLoginAndRender(user, pass);
  loginBtn.disabled = false;

  if (loginOk) {
    // Success
    loginScreen.classList.add('hidden');
    dashboard.classList.remove('hidden');
    loggedInUser.textContent = user;
    errMsg.textContent = '';
    usernameInput.value = '';
    pwInput.value = '';
    attempts = 0;
  } else {
    // Failure
    attempts++;
    const left = MAX_ATTEMPTS - attempts;

    if (left <= 0) {
      errMsg.textContent = 'Too many failed attempts. Access locked.';
      loginBtn.disabled = true;
      attemptsTxt.textContent = 'Refresh the page to try again.';
    } else {
      errMsg.textContent = 'Incorrect username or password.';
      attemptsTxt.textContent = left + ' attempt' + (left === 1 ? '' : 's') + ' remaining';
    }

    pwInput.value = '';
    pwInput.focus();
  }
}

loginBtn.addEventListener('click', doLogin);

pwInput.addEventListener('keydown', function (e) {
  if (e.key === 'Enter') doLogin();
});

usernameInput.addEventListener('keydown', function (e) {
  if (e.key === 'Enter') pwInput.focus();
});

// -------------------------------------------------
//  Show / hide password
// -------------------------------------------------
pwToggle.addEventListener('click', function () {
  const hidden = pwInput.type === 'password';
  pwInput.type = hidden ? 'text' : 'password';
  eyeIcon.className = hidden ? 'ti ti-eye-off' : 'ti ti-eye';
});

// -------------------------------------------------
//  Logout
// -------------------------------------------------
logoutBtn.addEventListener('click', function () {
  sessionStorage.removeItem('beamadminToken');
  dashboard.classList.add('hidden');
  loginScreen.classList.remove('hidden');
  errMsg.textContent = '';
  if (attempts < MAX_ATTEMPTS) {
    attemptsTxt.textContent = 'Use your admin login';
  }
  // Reset to dashboard page
  showPage('dashboard');
});

// -------------------------------------------------
//  Navigation
// -------------------------------------------------
const navItems = document.querySelectorAll('.nav-item[data-page]');
const pageDashboard = document.getElementById('page-dashboard');
const pageOther     = document.getElementById('page-other');
const placeholderTitle = document.getElementById('placeholder-title');

const pageLabels = {
  dashboard: 'Dashboard',
  players:   'Players',
  vehicles:  'Vehicles',
  maps:      'Maps',
  banlist:   'Ban list',
  settings:  'Settings',
  console:   'Console',
  logs:      'Logs'
};

function showPage(name) {
  navItems.forEach(function (btn) {
    btn.classList.toggle('active', btn.dataset.page === name);
  });

  pageTitle.textContent = pageLabels[name] || name;

  if (name === 'dashboard') {
    pageDashboard.classList.remove('hidden');
    pageOther.classList.add('hidden');
  } else {
    pageDashboard.classList.add('hidden');
    pageOther.classList.remove('hidden');
    placeholderTitle.textContent = '"' + pageLabels[name] + '" coming soon';
  }
}

navItems.forEach(function (btn) {
  btn.addEventListener('click', function () {
    showPage(btn.dataset.page);
  });
});

// -------------------------------------------------
//  BeamMP server overview
// -------------------------------------------------
const SERVER_IP = 'YOUR_VPS_PUBLIC_IP';
const SERVERS = [
  {
    id: 'offroad',
    name: 'Str1x3vo Offroad',
    path: '/opt/beammp-offroad',
    port: 30816,
    map: 'Reshjemheia',
    maxPlayers: 16,
    maxCars: 3,
    tags: ['Offroad', 'Freeroam'],
    status: 'online',
    note: 'Public stock offroad server',
    events: ['guest5050912 is now synced', 'Rules sent to guest5050912', 'Client connected']
  },
  {
    id: 'offroad-plus',
    name: 'Str1x3vo Offroad+',
    path: '/opt/beammp-offroad-plus',
    port: 30817,
    map: 'Johnson Valley',
    maxPlayers: 16,
    maxCars: 3,
    tags: ['Offroad', 'Freeroam'],
    status: 'online',
    note: 'Offroad plus with resource pack',
    events: ['Server listing updated', 'All systems started successfully', 'Gatekeeper loaded']
  },
  {
    id: 'vanilla',
    name: 'Str1x3vo Vanilla',
    path: '/opt/beammp-vanilla',
    port: 30814,
    map: 'Italy',
    maxPlayers: 16,
    maxCars: 2,
    tags: ['Freeroam'],
    status: 'online',
    note: 'Public stock freeroam server',
    events: ['Chill broadcast sent', 'Sticky nicks broadcasted', 'Server running']
  },
  {
    id: 'vanilla-plus',
    name: 'Str1x3vo Vanilla+',
    path: '/opt/beammp-vanilla-plus',
    port: 30815,
    map: 'West Coast USA',
    maxPlayers: 16,
    maxCars: 2,
    tags: ['Freeroam'],
    status: 'online',
    note: 'Freeroam plus with Str1x3vo resources',
    events: ['Recent players disconnected', 'Anti-grief warning sent', 'Auto broadcast active']
  },
  {
    id: 'highforce',
    name: 'Str1x3vo Highforce Custom BackRoadDriving UK',
    path: '/opt/beammp-highforce',
    port: 30818,
    map: 'High Force',
    maxPlayers: 16,
    maxCars: 6,
    tags: ['Backroads', 'UK', 'Custom'],
    status: 'online',
    note: 'Custom UK back road driving server',
    events: ['Server listing updated', 'All systems started successfully', 'Gatekeeper loaded']
  },
  {
    id: 'freeroam-old',
    name: 'Str1x3vo Public Freeroam',
    path: '/opt/beammp-server',
    port: 30814,
    map: 'West Coast USA',
    maxPlayers: 16,
    maxCars: 5,
    tags: ['Freeroam'],
    status: 'offline',
    note: 'Stopped; shares port 30814 with Vanilla',
    events: ['No running BeamMP process found', 'Last log activity was older than active servers']
  }
];

function addressFor(server) {
  return SERVER_IP + ':' + server.port;
}

function copyText(text, button) {
  navigator.clipboard.writeText(text).then(function () {
    const old = button.innerHTML;
    button.innerHTML = '<i class="ti ti-check"></i> Copied';
    setTimeout(function () {
      button.innerHTML = old;
    }, 1200);
  });
}

function renderServerDashboard() {
  const online = SERVERS.filter(function (server) { return server.status === 'online'; });
  const slots = SERVERS.reduce(function (sum, server) { return sum + server.maxPlayers; }, 0);

  pageDashboard.innerHTML = [
    '<div class="metrics">',
      '<div class="metric"><div class="metric-label">Servers online</div><div class="metric-value">' + online.length + ' <span class="metric-max">/' + SERVERS.length + '</span></div><div class="metric-sub">BeamMP fleet</div></div>',
      '<div class="metric"><div class="metric-label">Total slots</div><div class="metric-value">' + slots + '</div><div class="metric-sub">Across all configured servers</div></div>',
      '<div class="metric"><div class="metric-label">Public IP</div><div class="metric-value metric-value--sm">' + SERVER_IP + '</div><div class="metric-sub">Use IP:port in BeamMP</div></div>',
      '<div class="metric"><div class="metric-label">Admin path</div><div class="metric-value metric-value--sm">/opt/beamadmin</div><div class="metric-sub">Separate from BeamMP files</div></div>',
    '</div>',
    '<div class="section">',
      '<div class="section-header"><span class="section-title">BeamMP servers</span><button class="act-btn" id="copy-all-addresses"><i class="ti ti-copy"></i> Copy all</button></div>',
      '<div class="server-grid" id="server-grid"></div>',
    '</div>',
    '<div class="two-col">',
      '<div class="section"><div class="section-header"><span class="section-title">Recent events</span></div><div class="card"><div class="log-list" id="fleet-log"></div></div></div>',
      '<div class="section"><div class="section-header"><span class="section-title">Quick connect</span><button class="act-btn" id="copy-online-addresses"><i class="ti ti-copy-check"></i> Copy online</button></div><div class="card"><div class="quick-list" id="quick-list"></div></div></div>',
    '</div>'
  ].join('');

  const grid = document.getElementById('server-grid');
  grid.innerHTML = SERVERS.map(function (server) {
    const statusClass = server.status === 'online' ? 'badge-green' : 'badge-red';
    const tags = server.tags.map(function (tag) {
      return '<span class="server-tag">' + tag + '</span>';
    }).join('');

    return [
      '<article class="server-card">',
        '<div class="server-card-head">',
          '<div><h3>' + server.name + '</h3><p>' + server.note + '</p></div>',
          '<span class="badge ' + statusClass + '">' + server.status + '</span>',
        '</div>',
        '<div class="server-meta">',
          '<span><i class="ti ti-plug-connected"></i>' + addressFor(server) + '</span>',
          '<span><i class="ti ti-map"></i>' + server.map + '</span>',
          '<span><i class="ti ti-users"></i>' + server.maxPlayers + ' slots</span>',
          '<span><i class="ti ti-car"></i>' + server.maxCars + ' cars</span>',
        '</div>',
        '<div class="server-tags">' + tags + '</div>',
        '<div class="server-actions">',
          '<button class="act-btn copy-address" data-address="' + addressFor(server) + '"><i class="ti ti-copy"></i> Copy address</button>',
          '<button class="act-btn copy-path" data-address="' + server.path + '"><i class="ti ti-folder"></i> Copy path</button>',
        '</div>',
      '</article>'
    ].join('');
  }).join('');

  const log = document.getElementById('fleet-log');
  log.innerHTML = SERVERS.flatMap(function (server) {
    return server.events.slice(0, 2).map(function (event) {
      const cls = server.status === 'online' ? 'log-join' : 'log-warn';
      return '<div class="log-line"><span class="log-time">' + server.id + '</span><span class="' + cls + '">' + event + '</span></div>';
    });
  }).join('');

  const quickList = document.getElementById('quick-list');
  quickList.innerHTML = SERVERS.map(function (server) {
    return '<div class="quick-row"><span>' + server.name + '</span><code>' + addressFor(server) + '</code></div>';
  }).join('');

  document.querySelectorAll('.copy-address, .copy-path').forEach(function (button) {
    button.addEventListener('click', function () {
      copyText(button.dataset.address, button);
    });
  });

  document.getElementById('copy-all-addresses').addEventListener('click', function () {
    copyText(SERVERS.map(addressFor).join('\\n'), this);
  });

  document.getElementById('copy-online-addresses').addEventListener('click', function () {
    copyText(online.map(addressFor).join('\\n'), this);
  });

  const playersNav = document.querySelector('.nav-item[data-page="players"]');
  if (playersNav) {
    playersNav.innerHTML = '<i class="ti ti-server"></i> Servers <span class="badge badge-green ml-auto">' + online.length + '</span>';
  }

  const footer = document.querySelector('.status-txt');
  if (footer) footer.textContent = online.length + ' online';
}

const originalShowPage = showPage;
showPage = function (name) {
  if (name === 'players') name = 'dashboard';
  originalShowPage(name);
};

renderServerDashboard();

// -------------------------------------------------
//  Live admin API
// -------------------------------------------------
let apiToken = sessionStorage.getItem('beamadminToken') || '';
let refreshTimer = null;
const DISCORD_LINK = 'https://discord.gg/2WEntWFeQs';

const REASON_TEMPLATES = {
  kick: [
    'Ramming is not accepted on this server. Please rejoin and drive respectfully.',
    'Ignoring staff instructions. Please rejoin when you are ready to follow the rules.',
    'Blocking or disrupting other players. Please rejoin and keep it fair.',
    'AFK or inactive in a way that affects the server. You can rejoin when ready.'
  ],
  ban: [
    'Ramming is not accepted on this server. Appeal here: ' + DISCORD_LINK,
    'Repeated griefing after warnings. Appeal here: ' + DISCORD_LINK,
    'Harassment or abusive behavior toward other players. Appeal here: ' + DISCORD_LINK,
    'Bypassing rules or staff action. Appeal here: ' + DISCORD_LINK
  ]
};

async function apiRequest(path, options) {
  const opts = options || {};
  opts.headers = Object.assign({
    'Content-Type': 'application/json'
  }, opts.headers || {});

  if (apiToken) {
    opts.headers.Authorization = 'Bearer ' + apiToken;
  }

  const response = await fetch(path, opts);
  const payload = await response.json().catch(function () { return {}; });
  if (!response.ok) {
    const err = new Error(payload.error || 'Request failed');
    err.status = response.status;
    throw err;
  }
  return payload;
}

async function apiLoginAndRender(username, password) {
  try {
    const result = await apiRequest('/api/login', {
      method: 'POST',
      body: JSON.stringify({ username: username, password: password })
    });
    apiToken = result.token;
    sessionStorage.setItem('beamadminToken', apiToken);
    await loadLiveServers();
    if (refreshTimer) clearInterval(refreshTimer);
    refreshTimer = setInterval(loadLiveServers, 5000);
    return true;
  } catch (err) {
    return false;
  }
}

function htmlEscape(value) {
  return String(value == null ? '' : value)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}

function chooseReason(action) {
  const templates = REASON_TEMPLATES[action] || [];
  const lines = templates.map(function (text, index) {
    return (index + 1) + '. ' + text;
  });
  lines.push('C. Custom reason');

  const choice = prompt(
    (action === 'ban' ? 'Ban' : 'Kick') + ' reason template:\n\n' + lines.join('\n\n'),
    '1'
  );

  if (choice === null) return null;

  const normalized = choice.trim().toLowerCase();
  if (normalized === 'c' || normalized === 'custom') {
    return prompt(action === 'ban' ? 'Custom ban reason' : 'Custom kick reason', action === 'ban' ? 'Banned by admin. Appeal here: ' + DISCORD_LINK : 'Kicked by admin.');
  }

  const selected = Number(normalized);
  if (Number.isInteger(selected) && selected >= 1 && selected <= templates.length) {
    return templates[selected - 1];
  }

  return choice.trim();
}

async function loadLiveServers() {
  if (!apiToken) return;
  try {
    const payload = await apiRequest('/api/servers');
    renderLiveDashboard(payload.servers || []);
  } catch (err) {
    if (err.status === 401) {
      apiToken = '';
      sessionStorage.removeItem('beamadminToken');
      if (refreshTimer) clearInterval(refreshTimer);
      dashboard.classList.add('hidden');
      loginScreen.classList.remove('hidden');
      errMsg.textContent = 'Session expired. Sign in again.';
      return;
    }

    console.warn('BeamAdmin refresh failed:', err);
  }
}

function renderLiveDashboard(servers) {
  const online = servers.filter(function (server) { return server.online; });
  const slots = servers.reduce(function (sum, server) { return sum + Number(server.maxPlayers || 0); }, 0);
  const footer = document.querySelector('.status-txt');
  if (footer) footer.textContent = online.length + ' online';

  pageDashboard.innerHTML = [
    '<div class="metrics">',
      '<div class="metric"><div class="metric-label">Servers online</div><div class="metric-value">' + online.length + ' <span class="metric-max">/' + servers.length + '</span></div><div class="metric-sub">Bridge status</div></div>',
      '<div class="metric"><div class="metric-label">Players online</div><div class="metric-value">' + servers.reduce(function (sum, server) { return sum + Number((server.bridge || {}).playerCount || 0); }, 0) + ' <span class="metric-max">/' + slots + '</span></div><div class="metric-sub">Across all servers</div></div>',
      '<div class="metric"><div class="metric-label">Public IP</div><div class="metric-value metric-value--sm">' + SERVER_IP + '</div><div class="metric-sub">Use IP:port in BeamMP</div></div>',
      '<div class="metric"><div class="metric-label">Admin path</div><div class="metric-value metric-value--sm">/opt/beamadmin</div><div class="metric-sub">API + static UI</div></div>',
    '</div>',
    '<div class="section">',
      '<div class="section-header"><span class="section-title">BeamMP servers</span><button class="act-btn" id="copy-all-addresses"><i class="ti ti-copy"></i> Copy all</button></div>',
      '<div class="server-grid" id="server-grid"></div>',
    '</div>',
    '<div class="section">',
      '<div class="section-header"><span class="section-title">Live players</span><button class="act-btn" id="refresh-live"><i class="ti ti-refresh"></i> Refresh</button></div>',
      '<div class="card"><table class="player-table"><thead><tr><th>Server</th><th>Player</th><th>Server ID</th><th>Account</th><th>IP</th><th>Actions</th></tr></thead><tbody id="live-player-rows"></tbody></table></div>',
    '</div>'
  ].join('');

  const grid = document.getElementById('server-grid');
  grid.innerHTML = servers.map(function (server) {
    const statusClass = server.online ? 'badge-green' : 'badge-red';
    const statusText = server.online ? 'online' : 'offline';
    const tags = (server.tags || []).map(function (tag) {
      return '<span class="server-tag">' + htmlEscape(tag) + '</span>';
    }).join('');
    return [
      '<article class="server-card">',
        '<div class="server-card-head">',
          '<div><h3>' + htmlEscape(server.name) + '</h3><p>' + htmlEscape(server.note) + '</p></div>',
          '<span class="badge ' + statusClass + '">' + statusText + '</span>',
        '</div>',
        '<div class="server-meta">',
          '<span><i class="ti ti-plug-connected"></i>' + htmlEscape(server.address) + '</span>',
          '<span><i class="ti ti-map"></i>' + htmlEscape(server.map) + '</span>',
          '<span><i class="ti ti-users"></i>' + Number((server.bridge || {}).playerCount || 0) + ' / ' + Number(server.maxPlayers || 0) + '</span>',
          '<span><i class="ti ti-car"></i>' + Number(server.maxCars || 0) + ' cars</span>',
        '</div>',
        '<div class="server-tags">' + tags + '</div>',
        '<div class="server-actions">',
          '<button class="act-btn copy-address" data-address="' + htmlEscape(server.address) + '"><i class="ti ti-copy"></i> Copy address</button>',
          '<button class="act-btn copy-path" data-address="' + htmlEscape(server.path) + '"><i class="ti ti-folder"></i> Copy path</button>',
        '</div>',
      '</article>'
    ].join('');
  }).join('');

  const rows = [];
  servers.forEach(function (server) {
    const rawPlayers = (server.bridge || {}).players;
    const players = Array.isArray(rawPlayers) ? rawPlayers : Object.values(rawPlayers || {});
    players.forEach(function (player) {
      rows.push([
        '<tr>',
          '<td>' + htmlEscape(server.name) + '</td>',
          '<td><div class="player-name"><div class="avatar av-a">' + htmlEscape((player.name || '?').slice(0, 2).toUpperCase()) + '</div>' + htmlEscape(player.name) + '</div></td>',
          '<td><code>' + htmlEscape(player.serverPlayerId || player.id || '') + '</code></td>',
          '<td>' + htmlEscape(player.beammp || (player.isGuest ? 'Guest' : player.role || 'Unknown')) + '</td>',
          '<td>' + htmlEscape(player.ip || '') + '</td>',
          '<td><div class="row-actions">',
            '<button class="act-btn player-kick" data-server="' + htmlEscape(server.id) + '" data-id="' + htmlEscape(player.id) + '" data-name="' + htmlEscape(player.name) + '"><i class="ti ti-logout"></i> Kick</button>',
            '<button class="act-btn danger player-ban" data-server="' + htmlEscape(server.id) + '" data-id="' + htmlEscape(player.id) + '" data-name="' + htmlEscape(player.name) + '"><i class="ti ti-ban"></i> Ban</button>',
          '</div></td>',
        '</tr>'
      ].join(''));
    });
  });
  document.getElementById('live-player-rows').innerHTML = rows.length ? rows.join('') : '<tr><td colspan="6">No players reported by the bridge yet.</td></tr>';

  document.querySelectorAll('.copy-address, .copy-path').forEach(function (button) {
    button.addEventListener('click', function () { copyText(button.dataset.address, button); });
  });
  const copyAllButton = document.getElementById('copy-all-addresses');
  if (copyAllButton) {
    copyAllButton.addEventListener('click', function () {
      copyText(servers.map(function (server) { return server.address; }).join('\\n'), this);
    });
  }

  const refreshButton = document.getElementById('refresh-live');
  if (refreshButton) {
    refreshButton.addEventListener('click', loadLiveServers);
  }

  document.querySelectorAll('.player-kick, .player-ban').forEach(function (button) {
    button.addEventListener('click', async function () {
      const action = button.classList.contains('player-ban') ? 'ban' : 'kick';
      const reason = chooseReason(action);
      if (reason === null || reason.trim() === '') return;
      button.disabled = true;
      try {
        await apiRequest('/api/servers/' + button.dataset.server + '/' + action, {
          method: 'POST',
          body: JSON.stringify({ playerId: button.dataset.id, playerName: button.dataset.name, reason: reason })
        });
        button.innerHTML = '<i class="ti ti-check"></i> Queued';
        setTimeout(loadLiveServers, 2500);
      } catch (err) {
        alert(err.message);
      } finally {
        setTimeout(function () { button.disabled = false; }, 1200);
      }
    });
  });

  const playersNav = document.querySelector('.nav-item[data-page="players"]');
  if (playersNav) {
    playersNav.innerHTML = '<i class="ti ti-server"></i> Servers <span class="badge badge-green ml-auto">' + online.length + '</span>';
  }
}

attemptsTxt.textContent = 'Use your admin login';
