// MVC Prototype for WinRate AI

/* Model */
class AppModel {
  constructor() {
    this.user = null; // logged in user
    this.view = 'login';
    this.data = {
      stats: {
        wins: 24,
        losses: 12,
        winRate: '66%',
      },
      recentChampions: ['Ahri', 'Darius', 'Ashe'],
    };
  }

  login(username, password) {
    if (!username || !password) return { success: false, message: 'Both fields are required.' };
    if (username.length < 2 || password.length < 2) return { success: false, message: 'Username and password must be at least 2 characters long.' };
    this.user = { name: username };
    this.view = 'home';
    return { success: true, message: `Welcome, ${username}!` };
  }

  logout() {
    this.user = null;
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
          <label class="label" for="username">User</label>
          <input id="username" class="text-input" type="text" placeholder="Enter username" />
        </div>
        <div class="form-group">
          <label class="label" for="password">Password</label>
          <input id="password" class="text-input" type="password" placeholder="Enter password" />
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
        <p class="status">This is your WinRate dashboard prototype.</p>
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
    return `
      <section class="card">
        <h1 class="heading">Champions</h1>
        <p>Recent champions used:</p>
        <ul>${data.recentChampions.map(champ => `<li>${champ}</li>`).join('')}</ul>
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
    this.view.app.addEventListener('click', (e) => {
      const link = e.target.closest('[data-link]');
      if (link) {
        const viewName = link.getAttribute('data-link');
        this.model.navigate(viewName);
        this.view.render();
        return;
      }

      const action = e.target.getAttribute('data-action');
      if (action === 'login') {
        const username = document.getElementById('username').value.trim();
        const password = document.getElementById('password').value.trim();
        const result = this.model.login(username, password);
        const messageEl = document.getElementById('loginMessage');
        messageEl.innerText = result.message;
        messageEl.style.color = result.success ? '#2d7a3a' : '#b02a37';
        this.view.render();
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
