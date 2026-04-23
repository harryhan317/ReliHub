import React, { useState, useMemo } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { useAuthStore } from '../../store/authStore';
import { useUIStore } from '../../store/uiStore';
import { Button } from '../../components/ui/Button';
import { Input, InputGroup, InputLabel } from '../../components/ui/Input';
import { Checkbox } from '../../components/ui/Common';

const PHONE_REGEX = /^1[3-9]\d{9}$/;
const PASSWORD_RULES = {
  minLength: 8,
  maxLength: 20,
  patterns: [
    { regex: /[a-z]/, label: '小写字母' },
    { regex: /[A-Z]/, label: '大写字母' },
    { regex: /\d/, label: '数字' },
    { regex: /[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?]/, label: '特殊符号' },
  ],
  minCategories: 2,
};

function validatePassword(pwd: string): { valid: boolean; message: string } {
  if (pwd.length < PASSWORD_RULES.minLength || pwd.length > PASSWORD_RULES.maxLength) {
    return { valid: false, message: `密码长度需${PASSWORD_RULES.minLength}~${PASSWORD_RULES.maxLength}位` };
  }
  const matchedCategories = PASSWORD_RULES.patterns.filter((p) => p.regex.test(pwd)).length;
  if (matchedCategories < PASSWORD_RULES.minCategories) {
    return { valid: false, message: '密码需包含大小写字母、数字、特殊符号中至少2项' };
  }
  return { valid: true, message: '' };
}

const LoginPage: React.FC = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const { login, loginByCode } = useAuthStore();
  const { showToast } = useUIStore();

  const sourceScene = searchParams.get('source_scene') || '';
  const triggerAction = searchParams.get('trigger_action') || '';
  const returnTab = searchParams.get('return_tab') || '';
  const triggerTime = searchParams.get('trigger_time') || '';

  const [activeTab, setActiveTab] = useState<'code' | 'password'>('code');
  const [phone, setPhone] = useState('');
  const [code, setCode] = useState('');
  const [password, setPassword] = useState('');
  const [agreed, setAgreed] = useState(false);
  const [agreedShake, setAgreedShake] = useState(false);
  const [countdown, setCountdown] = useState(0);
  const [passwordError, setPasswordError] = useState('');

  const isTriggerExpired = useMemo(() => {
    if (!triggerTime) return false;
    const elapsed = Date.now() - new Date(triggerTime).getTime();
    return elapsed > 15 * 60 * 1000;
  }, [triggerTime]);

  const navigateAfterLogin = (isNewUser: boolean) => {
    if (isNewUser) {
      navigate('/profile-setup', { replace: true });
      return;
    }

    if (triggerAction && !isTriggerExpired) {
      const routeMap: Record<string, string> = {
        download: '/resource',
        comment: '/community',
        open_my: '/my',
        upload: '/resource/upload',
        new_topic: '/community/new-topic',
        ai_limit: '/ask',
        resource_limit: '/resource',
        community_limit: '/community',
        like: '/community',
        collect: '/resource',
        reply: '/community',
        report: '/community',
      };
      navigate(routeMap[triggerAction] || '/ask', { replace: true });
      return;
    }

    if (returnTab) {
      const tabRouteMap: Record<string, string> = {
        ask: '/ask',
        resource: '/resource',
        community: '/community',
        my: '/my',
      };
      navigate(tabRouteMap[returnTab] || '/ask', { replace: true });
      return;
    }

    navigate('/ask', { replace: true });
  };

  const handleAgreedBlock = (): boolean => {
    if (!agreed) {
      setAgreedShake(true);
      setTimeout(() => setAgreedShake(false), 600);
      showToast('请先同意用户协议和隐私政策', 'error');
      return true;
    }
    return false;
  };

  const handleSendCode = () => {
    if (handleAgreedBlock()) return;
    if (!phone) {
      showToast('请输入手机号', 'error');
      return;
    }
    if (!PHONE_REGEX.test(phone)) {
      showToast('请输入正确的手机号', 'error');
      return;
    }
    setCountdown(60);
    const timer = setInterval(() => {
      setCountdown((prev) => {
        if (prev <= 1) {
          clearInterval(timer);
          return 0;
        }
        return prev - 1;
      });
    }, 1000);
    showToast('验证码已发送', 'success');
  };

  const handleLogin = async () => {
    if (handleAgreedBlock()) return;

    try {
      let result;
      if (activeTab === 'code') {
        if (!phone || !code) {
          showToast('请输入手机号和验证码', 'error');
          return;
        }
        result = await loginByCode(phone, code);
      } else {
        if (!phone || !password) {
          showToast('请输入手机号和密码', 'error');
          return;
        }
        const pwdCheck = validatePassword(password);
        if (!pwdCheck.valid) {
          setPasswordError(pwdCheck.message);
          return;
        }
        result = await login(phone, password);
      }
      showToast('登录成功！欢迎回来', 'success');
      navigateAfterLogin(result?.is_new_user || false);
    } catch (err: any) {
      showToast(err.message || '登录失败', 'error');
    }
  };

  const handleWechatLogin = async () => {
    if (handleAgreedBlock()) return;
    showToast('微信登录功能开发中', 'info');
  };

  return (
    <div className="page active">
      <div className="mesh-bg" />
      <div className="top-bar" style={{ background: 'transparent', border: 'none' }}>
        <button className="top-bar-btn" onClick={() => navigate(-1)}>←</button>
        <div className="top-bar-title" />
        <div style={{ width: 32 }} />
      </div>
      <div className="login-header">
        <div className="login-logo">R</div>
        <div className="login-title gradient-text">欢迎来到 ReliHub</div>
        <div className="login-subtitle">登录或注册，开启可靠性之旅</div>
      </div>
      <div className="login-form">
        <div className="login-tabs">
          <button
            className={`login-tab ${activeTab === 'code' ? 'active' : ''}`}
            onClick={() => setActiveTab('code')}
          >
            验证码登录
          </button>
          <button
            className={`login-tab ${activeTab === 'password' ? 'active' : ''}`}
            onClick={() => setActiveTab('password')}
          >
            密码登录
          </button>
        </div>

        {activeTab === 'code' && (
          <div className="login-panel active">
            <div className="input-group">
              <div className="phone-input-row">
                <span className="phone-prefix">+86</span>
                <Input
                  type="tel"
                  placeholder="请输入手机号"
                  maxLength={11}
                  value={phone}
                  onChange={(e) => setPhone(e.target.value)}
                />
              </div>
            </div>
            <div className="input-group">
              <div className="code-input-row">
                <Input
                  type="text"
                  placeholder="请输入验证码"
                  maxLength={6}
                  value={code}
                  onChange={(e) => setCode(e.target.value)}
                />
                <button
                  className="send-code-btn"
                  onClick={handleSendCode}
                  disabled={countdown > 0}
                  style={{ opacity: countdown > 0 ? 0.5 : 1 }}
                >
                  {countdown > 0 ? `${countdown}s` : '获取验证码'}
                </button>
              </div>
            </div>
            <div className={`agreement-row ${agreedShake ? 'shake' : ''}`}>
              <Checkbox checked={agreed} onToggle={() => setAgreed(!agreed)} />
              <span>我已阅读并同意 <a href="#">《用户协议》</a>和<a href="#">《隐私政策》</a></span>
            </div>
            <Button variant="primary" block size="lg" onClick={handleLogin}>登录 / 注册</Button>
          </div>
        )}

        {activeTab === 'password' && (
          <div className="login-panel active">
            <div className="input-group">
              <div className="phone-input-row">
                <span className="phone-prefix">+86</span>
                <Input
                  type="tel"
                  placeholder="请输入手机号"
                  maxLength={11}
                  value={phone}
                  onChange={(e) => setPhone(e.target.value)}
                />
              </div>
            </div>
            <div className="input-group">
              <Input
                type="password"
                placeholder="请输入密码"
                value={password}
                onChange={(e) => { setPassword(e.target.value); setPasswordError(''); }}
              />
              {passwordError && (
                <div style={{ fontSize: 'var(--font-size-small)', color: 'var(--color-error)', marginTop: 4 }}>{passwordError}</div>
              )}
              <div className="forgot-password" onClick={() => navigate('/forgot-password')}>忘记密码？</div>
            </div>
            <div className={`agreement-row ${agreedShake ? 'shake' : ''}`}>
              <Checkbox checked={agreed} onToggle={() => setAgreed(!agreed)} />
              <span>我已阅读并同意 <a href="#">《用户协议》</a>和<a href="#">《隐私政策》</a></span>
            </div>
            <Button variant="primary" block size="lg" onClick={handleLogin}>登录</Button>
          </div>
        )}

        <div className="divider-with-text">其他登录方式</div>
        <div className="wechat-login-section">
          <Button variant="wechat" block size="lg" onClick={handleWechatLogin}>
            <span style={{ fontSize: '18px', fontWeight: 'bold', color: '#ffffff' }}>💚</span> 微信一键登录
          </Button>
        </div>
      </div>
    </div>
  );
};

export default LoginPage;
