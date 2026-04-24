const App = {
  currentPage: null,
  pageHistory: [],
  searchState: {
    query: '',
    type: 'RESOURCE',
    history: ['电容降额设计规范', 'HALT测试流程', 'FMEA分析方法'],
  },
  userState: {
    isGuest: true,
    isLoggedIn: false,
    isNewUser: false,
    phone: '',
    nickname: '',
    avatar: '',
    level: '新兵',
    creditScore: 50,
    cocoaBeans: 0,
    checkedInToday: false,
    earlyBirdAvailable: true,
    earlyBirdCount: 47,
  },

  init() {
    this.bindNavEvents();
    this.bindGlobalEvents();
    this.bindSearchEvents();
    this.navigateTo('welcome');
  },

  bindNavEvents() {
    document.querySelectorAll('.nav-item').forEach(item => {
      item.addEventListener('click', () => {
        const tab = item.dataset.tab;
        if (tab === 'my' && this.userState.isGuest) {
          this.showRegisterGuide('open_my');
          return;
        }
        this.switchTab(tab);
      });
    });
  },

  bindGlobalEvents() {
    document.addEventListener('click', (e) => {
      const actionEl = e.target.closest('[data-action]');
      if (actionEl) {
        e.preventDefault();
        const actionName = actionEl.dataset.action;
        const param = actionEl.dataset.param;
        this.handleAction(actionName, param, actionEl);
      }
    });

    document.querySelectorAll('.modal-overlay').forEach(modal => {
      modal.addEventListener('click', (e) => {
        if (e.target === modal) {
          modal.classList.remove('active');
        }
      });
    });
  },

  bindSearchEvents() {
    const searchInput = document.getElementById('search-input');
    const searchClear = document.getElementById('search-clear');
    const searchSubmit = document.getElementById('search-submit');
    const clearHistory = document.getElementById('clear-search-history');

    if (searchInput) {
      searchInput.addEventListener('input', () => {
        if (searchClear) searchClear.style.display = searchInput.value ? 'flex' : 'none';
      });
      searchInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && searchInput.value.trim()) {
          this.executeSearch(searchInput.value.trim());
        }
      });
    }

    if (searchClear) {
      searchClear.addEventListener('click', () => {
        if (searchInput) {
          searchInput.value = '';
          searchInput.focus();
          searchClear.style.display = 'none';
        }
        document.getElementById('search-hot').style.display = '';
        document.getElementById('search-results').style.display = 'none';
        document.getElementById('search-empty').style.display = 'none';
      });
    }

    if (searchSubmit) {
      searchSubmit.addEventListener('click', () => {
        if (searchInput && searchInput.value.trim()) {
          this.executeSearch(searchInput.value.trim());
        }
      });
    }

    if (clearHistory) {
      clearHistory.addEventListener('click', () => {
        this.searchState.history = [];
        const list = document.getElementById('search-history-list');
        if (list) list.innerHTML = '<div style="font-size:var(--font-size-caption);color:var(--color-text-muted);text-align:center;padding:var(--spacing-lg);">暂无搜索历史</div>';
      });
    }

    document.querySelectorAll('#search-hot .tag').forEach(tag => {
      tag.addEventListener('click', () => {
        const keyword = tag.textContent.trim();
        if (searchInput) searchInput.value = keyword;
        this.executeSearch(keyword);
      });
    });
  },

  executeSearch(query) {
    this.searchState.query = query;
    if (!this.searchState.history.includes(query)) {
      this.searchState.history.unshift(query);
      if (this.searchState.history.length > 10) this.searchState.history.pop();
    }

    document.getElementById('search-hot').style.display = 'none';
    document.getElementById('search-results').style.display = '';
    document.getElementById('search-empty').style.display = 'none';
  },

  handleAction(action, param, el) {
    switch (action) {
      case 'navigate':
        this.navigateTo(param);
        break;
      case 'back':
        this.goBack();
        break;
      case 'switch-tab':
        if (param === 'my' && this.userState.isGuest) {
          this.showRegisterGuide('open_my');
          return;
        }
        this.switchTab(param);
        break;
      case 'show-modal':
        this.showModal(param);
        break;
      case 'hide-modal':
        this.hideModal(param);
        break;
      case 'show-register-guide':
        this.showRegisterGuide(param);
        break;
      case 'login':
        this.handleLogin();
        break;
      case 'register':
        this.handleRegister();
        break;
      case 'send-code':
        this.handleSendCode(el);
        break;
      case 'toggle-checkbox':
        this.toggleCheckbox(el);
        break;
      case 'toggle-switch':
        this.toggleSwitch(el);
        break;
      case 'checkin':
        this.handleCheckin();
        break;
      case 'tab-switch':
        this.handleTabSwitch(el, param);
        break;
      case 'search-tab':
        this.handleSearchTab(el);
        break;
      case 'show-toast':
        this.showToast(param, 'info');
        break;
      case 'delete-item':
        this.handleDelete(el);
        break;
      case 'like':
        this.handleLike(el);
        break;
      case 'dislike':
        this.handleDislike(el);
        break;
      case 'download':
        this.handleDownload(param);
        break;
      case 'collect':
        this.handleCollect(el);
        break;
      case 'follow':
        this.handleFollow(el);
        break;
      case 'bounty':
        this.handleBounty();
        break;
      case 'adopt':
        this.handleAdopt(el);
        break;
      case 'share':
        this.handleShare();
        break;
      case 'report':
        this.handleReport();
        break;
      case 'open-search':
        this.openSearch(param);
        break;
      case 'delete-search-history':
        this.deleteSearchHistory(el);
        break;
      default:
        break;
    }
  },

  navigateTo(pageId) {
    const guestRestrictedPages = ['page-resource-upload', 'page-new-topic', 'page-profile-edit'];
    if (this.userState.isGuest && guestRestrictedPages.includes(pageId)) {
      this.showRegisterGuide('navigate_' + pageId);
      return;
    }

    const pages = document.querySelectorAll('.page');
    const targetPage = document.getElementById(pageId);
    if (!targetPage) return;

    if (this.currentPage && this.currentPage !== pageId) {
      this.pageHistory.push(this.currentPage);
    }

    pages.forEach(p => {
      p.classList.remove('active', 'page-slide-in', 'page-slide-out');
    });

    targetPage.classList.add('active', 'page-slide-in');
    this.currentPage = pageId;
    targetPage.scrollTop = 0;

    this.updatePageState(pageId);
  },

  updatePageState(pageId) {
    if (pageId === 'page-my' && this.userState.isLoggedIn) {
      const nickname = document.getElementById('my-nickname');
      const level = document.getElementById('my-level');
      const beans = document.getElementById('my-beans');
      const credit = document.getElementById('my-credit');
      const loginBtn = document.getElementById('my-login-btn');

      if (nickname) nickname.textContent = this.userState.nickname || '可靠性工程师';
      if (level) level.textContent = `Lv.${this.userState.creditScore >= 80 ? '专家' : this.userState.creditScore >= 60 ? '老兵' : '新兵'} · 信誉 ${this.userState.creditScore}`;
      if (beans) beans.textContent = this.userState.cocoaBeans;
      if (credit) credit.textContent = this.userState.creditScore;
      if (loginBtn) {
        loginBtn.textContent = '编辑资料';
        loginBtn.dataset.param = 'page-profile-edit';
      }
    }
  },

  goBack() {
    if (this.pageHistory.length > 0) {
      const prevPage = this.pageHistory.pop();
      const pages = document.querySelectorAll('.page');
      pages.forEach(p => {
        p.classList.remove('active', 'page-slide-in', 'page-slide-out');
      });
      const targetPage = document.getElementById(prevPage);
      if (targetPage) {
        targetPage.classList.add('active');
        this.currentPage = prevPage;
      }
    }
  },

  switchTab(tab) {
    document.querySelectorAll('.nav-item').forEach(item => {
      item.classList.toggle('active', item.dataset.tab === tab);
    });

    const tabMap = {
      'ask': 'page-ask',
      'resource': 'page-resource',
      'community': 'page-community',
      'my': 'page-my'
    };

    const pageId = tabMap[tab];
    if (pageId) {
      this.pageHistory = [];
      const pages = document.querySelectorAll('.page');
      pages.forEach(p => {
        p.classList.remove('active', 'page-slide-in', 'page-slide-out');
      });
      const targetPage = document.getElementById(pageId);
      if (targetPage) {
        targetPage.classList.add('active');
        this.currentPage = pageId;
        targetPage.scrollTop = 0;
      }
    }
  },

  showModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
      modal.classList.add('active');
    }
  },

  hideModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
      modal.classList.remove('active');
    }
  },

  showRegisterGuide(source) {
    this.showModal('modal-register-guide');
    const guideModal = document.getElementById('modal-register-guide');
    if (guideModal) {
      guideModal.dataset.source = source || '';
    }
  },

  handleLogin() {
    this.userState.isGuest = false;
    this.userState.isLoggedIn = true;
    this.userState.nickname = '可靠性工程师';
    this.userState.cocoaBeans = 50;
    this.userState.creditScore = 50;
    this.hideModal('modal-register-guide');
    this.updateGuestBanners();
    this.switchTab('ask');
    this.showToast('登录成功！欢迎回来', 'success');
  },

  handleRegister() {
    this.userState.isGuest = false;
    this.userState.isLoggedIn = true;
    this.userState.isNewUser = true;
    this.userState.cocoaBeans = 30;
    if (this.userState.earlyBirdAvailable) {
      this.userState.cocoaBeans += 20;
    }
    this.userState.creditScore = 50;
    this.userState.nickname = '新用户';
    this.hideModal('modal-register-guide');
    this.updateGuestBanners();
    this.navigateTo('page-profile-setup');
    this.showToast('注册成功！获得50可可豆早鸟奖励 🎉', 'success');
  },

  updateGuestBanners() {
    if (!this.userState.isGuest) {
      document.querySelectorAll('.guest-banner').forEach(banner => {
        banner.style.transition = 'all 0.3s ease';
        banner.style.maxHeight = '0';
        banner.style.padding = '0';
        banner.style.overflow = 'hidden';
        banner.style.opacity = '0';
        setTimeout(() => banner.style.display = 'none', 300);
      });
    }
  },

  handleSendCode(el) {
    const phoneInput = el.closest('.login-form, .login-panel')?.querySelector('.input-field');
    if (phoneInput && !phoneInput.value) {
      phoneInput.classList.add('error');
      this.showToast('请输入手机号', 'error');
      setTimeout(() => phoneInput.classList.remove('error'), 2000);
      return;
    }

    let seconds = 60;
    const originalText = el.textContent;
    el.disabled = true;
    el.style.opacity = '0.5';
    const timer = setInterval(() => {
      seconds--;
      el.textContent = `${seconds}s`;
      if (seconds <= 0) {
        clearInterval(timer);
        el.textContent = originalText;
        el.disabled = false;
        el.style.opacity = '1';
      }
    }, 1000);
    this.showToast('验证码已发送', 'success');
  },

  toggleCheckbox(el) {
    const checkbox = el.closest('.checkbox-wrapper')?.querySelector('.checkbox') || el.querySelector('.checkbox') || el;
    checkbox.classList.toggle('checked');
  },

  toggleSwitch(el) {
    el.classList.toggle('on');
  },

  handleCheckin() {
    if (this.userState.isGuest) {
      this.showRegisterGuide('checkin');
      return;
    }
    if (this.userState.checkedInToday) {
      this.showToast('今天已经签到过了', 'info');
      return;
    }
    this.userState.checkedInToday = true;
    this.userState.cocoaBeans += 2;
    this.userState.creditScore += 1;
    this.showToast('签到成功！+2🫘 +1信誉分', 'success');
    const checkinBtn = document.getElementById('checkin-btn');
    if (checkinBtn) {
      checkinBtn.textContent = '已签到 ✓';
      checkinBtn.classList.add('btn-disabled');
    }
    const todayDot = document.querySelector('.streak-day.today');
    if (todayDot) todayDot.classList.add('checked');
  },

  handleTabSwitch(el, group) {
    const tabBar = el.closest('.tab-bar');
    if (!tabBar) return;
    const tabs = tabBar.querySelectorAll('.tab-item');
    const index = Array.from(tabs).indexOf(el);
    tabs.forEach(t => t.classList.remove('active'));
    el.classList.add('active');

    const indicator = tabBar.querySelector('.tab-indicator');
    if (indicator) {
      const width = 100 / tabs.length;
      indicator.style.left = `${index * width}%`;
      indicator.style.width = `${width}%`;
    }
  },

  handleSearchTab(el) {
    const tabBar = el.closest('.tab-bar');
    if (!tabBar) return;
    const tabs = tabBar.querySelectorAll('.tab-item');
    const index = Array.from(tabs).indexOf(el);
    tabs.forEach(t => t.classList.remove('active'));
    el.classList.add('active');

    this.searchState.type = el.dataset.type || 'RESOURCE';

    const indicator = tabBar.querySelector('.tab-indicator');
    if (indicator) {
      const width = 100 / tabs.length;
      indicator.style.left = `${index * width}%`;
      indicator.style.width = `${width}%`;
    }

    const searchInput = document.getElementById('search-input');
    if (searchInput) {
      const placeholders = {
        'RESOURCE': '搜索资源标题/关键词',
        'COMMUNITY': '搜索话题标题/内容',
        'AI': '搜索我的对话'
      };
      searchInput.placeholder = placeholders[this.searchState.type] || '搜索';
    }

    if (this.searchState.query) {
      this.executeSearch(this.searchState.query);
    }
  },

  openSearch(type) {
    this.searchState.type = type || 'RESOURCE';
    this.navigateTo('page-search');

    const searchInput = document.getElementById('search-input');
    const placeholders = {
      'RESOURCE': '搜索资源标题/关键词',
      'COMMUNITY': '搜索话题标题/内容',
      'AI': '搜索我的对话'
    };
    if (searchInput) {
      searchInput.placeholder = placeholders[this.searchState.type] || '搜索';
      searchInput.value = '';
      searchInput.focus();
    }

    document.getElementById('search-hot').style.display = '';
    document.getElementById('search-results').style.display = 'none';
    document.getElementById('search-empty').style.display = 'none';

    const searchTabs = document.querySelectorAll('#search-tabs .tab-item');
    searchTabs.forEach(t => {
      t.classList.toggle('active', t.dataset.type === this.searchState.type);
    });
    const tabIndex = Array.from(searchTabs).findIndex(t => t.dataset.type === this.searchState.type);
    const indicator = document.querySelector('#search-tabs .tab-indicator');
    if (indicator && tabIndex >= 0) {
      indicator.style.left = `${tabIndex * 33.33}%`;
      indicator.style.width = '33.33%';
    }
  },

  deleteSearchHistory(el) {
    const item = el.closest('.history-item');
    if (item) {
      item.style.transition = 'all 0.3s ease';
      item.style.transform = 'translateX(100%)';
      item.style.opacity = '0';
      setTimeout(() => item.remove(), 300);
    }
  },

  handleLike(el) {
    if (this.userState.isGuest) {
      this.showRegisterGuide('like');
      return;
    }
    el.classList.toggle('active');
    if (el.classList.contains('active')) {
      el.style.color = 'var(--color-accent)';
      this.showToast('已点赞', 'success');
    } else {
      el.style.color = '';
    }
  },

  handleDislike(el) {
    if (this.userState.isGuest) {
      this.showRegisterGuide('dislike');
      return;
    }
    el.classList.toggle('active');
    if (el.classList.contains('active')) {
      el.style.color = 'var(--color-error)';
    } else {
      el.style.color = '';
    }
  },

  handleDownload(resourceId) {
    if (this.userState.isGuest) {
      this.showRegisterGuide('download');
      return;
    }
    this.showModal('modal-download-confirm');
  },

  handleCollect(el) {
    if (this.userState.isGuest) {
      this.showRegisterGuide('collect');
      return;
    }
    el.classList.toggle('active');
    if (el.classList.contains('active')) {
      el.style.color = 'var(--color-warning)';
      this.showToast('已收藏', 'success');
    } else {
      el.style.color = '';
      this.showToast('已取消收藏', 'info');
    }
  },

  handleFollow(el) {
    if (this.userState.isGuest) {
      this.showRegisterGuide('follow');
      return;
    }
    el.classList.toggle('active');
    if (el.classList.contains('active')) {
      el.textContent = '已关注';
      el.classList.remove('btn-ghost');
      el.classList.add('btn-secondary', 'btn-sm');
    } else {
      el.textContent = '+关注';
      el.classList.add('btn-ghost');
      el.classList.remove('btn-secondary');
    }
  },

  handleBounty() {
    if (this.userState.isGuest) {
      this.showRegisterGuide('bounty');
      return;
    }
    this.showToast('悬赏功能开发中', 'info');
  },

  handleAdopt(el) {
    this.showToast('已采纳为最佳回答', 'success');
  },

  handleShare() {
    this.showToast('分享功能开发中', 'info');
  },

  handleReport() {
    if (this.userState.isGuest) {
      this.showRegisterGuide('report');
      return;
    }
    this.showToast('举报已提交，我们会尽快处理', 'success');
  },

  handleDelete(el) {
    const item = el.closest('.list-item, .chat-item, .history-item');
    if (item) {
      item.style.transition = 'all 0.3s ease';
      item.style.transform = 'translateX(100%)';
      item.style.opacity = '0';
      setTimeout(() => item.remove(), 300);
    }
  },

  showToast(message, type = 'info') {
    const screen = document.querySelector('.phone-screen');
    if (!screen) return;

    const existing = screen.querySelector('.toast');
    if (existing) existing.remove();

    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.textContent = message;
    screen.appendChild(toast);

    setTimeout(() => {
      if (toast.parentNode) toast.remove();
    }, 2500);
  },

  simulateTyping(container, text, callback) {
    let index = 0;
    const interval = setInterval(() => {
      if (index < text.length) {
        container.textContent += text[index];
        index++;
      } else {
        clearInterval(interval);
        if (callback) callback();
      }
    }, 30);
  }
};

document.addEventListener('DOMContentLoaded', () => {
  App.init();
});
