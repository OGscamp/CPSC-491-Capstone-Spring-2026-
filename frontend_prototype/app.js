// MVC Prototype for WinRate AI

/* Model */
class AppModel {
  constructor() {
    this.user = null; // logged in user
    this.view = 'login';
    this.puuid = null;
    this.data = {
      stats: { wins: 0, losses: 0, winRate: '0%' },
      matches: [],
      loading: false,
      error: null,
    };
  }

  async login(username, tagLine) {
    if (!username || !tagLine) return { success: false, message: 'Both fields are required.' };
    if (username.length < 2 || tagLine.length < 1) return { success: false, message: 'Username and tag must be at least 2 characters long.' };
    this.data.loading = true;
    this.data.error = null;
    try {
      const resp = await fetch(
        `http://localhost:5000/api/player/${encodeURIComponent(username)}/${encodeURIComponent(tagLine)}`
      );
      if (!resp.ok) {
        const err = await resp.json();
        this.data.loading = false;
        this.data.error = err.error || 'Player not found.';
        return { success: false, message: this.data.error };
      }
      const data = await resp.json();
      this.puuid = data.puuid;
      this.user = { name: data.summoner_name };
      this.data.stats = { wins: data.wins, losses: data.losses, winRate: data.win_rate };
      this.data.loading = false;
      this.view = 'home';
      return { success: true, message: `Welcome, ${data.summoner_name}!` };
    } catch (e) {
      this.data.loading = false;
      return { success: false, message: 'Server unavailable. Is the Flask server running?' };
    }
  }

  async loadMatches() {
    if (!this.puuid) return;
    this.data.loading = true;
    try {
      const resp = await fetch(`http://localhost:5000/api/matches/${encodeURIComponent(this.puuid)}`);
      if (resp.ok) {
        const data = await resp.json();
        this.data.matches = data.matches || [];
      }
    } catch (e) {
      this.data.error = 'Could not load match history.';
    } finally {
      this.data.loading = false;
    }
  }

  logout() {
    this.user = null;
    this.puuid = null;
    this.data.matches = [];
    this.view = 'login';
  }

  navigate(viewName) {
    if (!this.user && viewName !== 'login') {
      this.view = 'login';
      return;
    }
    this.view = viewName;
  }
}

/* View */
class AppView {
  constructor(model) {
    this.model = model;
    this.app = document.getElementById('app');
  }

  render() {
    const { user, view, data } = this.model;

    const nav = `
      <header class="navbar">
        <div class="brand">WinRate AI</div>
        <nav class="nav-links">
          <a class="nav-link ${view === 'home' ? 'active' : ''}" data-link="home">Home</a>
          <a class="nav-link ${view === 'profile' ? 'active' : ''}" data-link="profile">Profile</a>
          <a class="nav-link ${view === 'champions' ? 'active' : ''}" data-link="champions">Champions</a>
          <a class="nav-link ${view === 'tier' ? 'active' : ''}" data-link="tier">Tier List</a>
        </nav>
        <div class="auth-buttons">
          ${user ? `<button class="button secondary" data-action="logout">Logout</button>` : ''}
        </div>
      </header>
    `;

    let mainContent;
    if (!user && view === 'login') {
      mainContent = this.loginTemplate();
    } else if (user && view === 'home') {
      mainContent = this.homeTemplate(data, user);
    } else if (user && view === 'profile') {
      mainContent = this.profileTemplate(user);
    } else if (user && view === 'champions') {
      mainContent = this.championsTemplate(data);
    } else if (user && view === 'tier') {
      mainContent = this.tierTemplate();
    } else {
      mainContent = '<div class="card"><p class="status">This view is not available.</p></div>';
    }

    this.app.innerHTML = `${nav}<main class="main">${mainContent}</main>`;
  }

  loginTemplate() {
    return `
      <section class="card">
        <h1 class="heading">Sign in</h1>
        <div class="form-group">
          <label class="label" for="username">Summoner Name</label>
          <input id="username" class="text-input" type="text" placeholder="Enter summoner name" />
        </div>
        <div class="form-group">
          <label class="label" for="password">Tag (e.g. NA1)</label>
          <input id="password" class="text-input" type="text" placeholder="Enter tag line" />
        </div>
        <button class="button" data-action="login">Sign In</button>
        <p id="loginMessage" class="status"></p>
      </section>
    `;
  }

  homeTemplate(data, user) {
    return `
      <section class="card">
        <h1 class="heading">Welcome ${user.name}</h1>
        <p class="status">This is your WinRate dashboard.</p>
      </section>
      <div class="dashboard-grid">
        <div class="card small">
          <h3>Win Rate</h3>
          <p>${data.stats.winRate}</p>
        </div>
        <div class="card small">
          <h3>Wins</h3>
          <p>${data.stats.wins}</p>
        </div>
        <div class="card small">
          <h3>Losses</h3>
          <p>${data.stats.losses}</p>
        </div>
      </div>
    `;
  }

  profileTemplate(user) {
    return `
      <section class="card">
        <h1 class="heading">Profile</h1>
        <p><strong>Username:</strong> ${user.name}</p>
        <p><strong>Email:</strong> user@winrate.ai</p>
      </section>
    `;
  }

  championsTemplate(data) {
    if (data.loading) {
      return `<section class="card"><p class="status">Loading match history...</p></section>`;
    }
    const matchList = data.matches.length > 0
      ? data.matches.map(m => `
          <li>
            <strong>${m.match_id}</strong>
            &mdash; ${m.game_date ? m.game_date.slice(0, 10) : 'Unknown date'}
            &mdash; ${Math.floor((m.game_length || 0) / 60)}m
            &mdash; Winner: Team ${m.winning_team || '?'}
          </li>`).join('')
      : '<li>No matches found.</li>';
    return `
      <section class="card">
        <h1 class="heading">Match History</h1>
        <ul>${matchList}</ul>
      </section>
    `;
  }

  tierTemplate() {
    return `
      <section class="card">
        <h1 class="heading">Tier List</h1>
        <p>Placeholder content for tier list skills and integration with backend API later.</p>
      </section>
    `;
  }
}

/* Controller */
class AppController {
  constructor(model, view) {
    this.model = model;
    this.view = view;
    this.init();
  }

  init() {
    this.view.render();
    this.addEventListeners();
  }

  addEventListeners() {
    this.view.app.addEventListener('click', async (e) => {
      const link = e.target.closest('[data-link]');
      if (link) {
        const viewName = link.getAttribute('data-link');
        this.model.navigate(viewName);
        this.view.render();
        if (viewName === 'champions' && this.model.puuid) {
          this.model.loadMatches().then(() => this.view.render());
        }
        return;
      }

      const action = e.target.getAttribute('data-action');
      if (action === 'login') {
        const username = document.getElementById('username').value.trim();
        const tagLine  = document.getElementById('password').value.trim();
        const messageEl = document.getElementById('loginMessage');
        messageEl.innerText = 'Signing in...';
        messageEl.style.color = '#555';
        const result = await this.model.login(username, tagLine);
        messageEl.innerText = result.message;
        messageEl.style.color = result.success ? '#2d7a3a' : '#b02a37';
        if (result.success) this.view.render();
        return;
      }

      if (action === 'logout') {
        this.model.logout();
        this.view.render();
      }
    });
  }
}

const appModel = new AppModel();
const appView = new AppView(appModel);
new AppController(appModel, appView);
