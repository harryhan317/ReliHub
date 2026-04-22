import { act, renderHook } from '@testing-library/react';
import { useAuthStore } from '../authStore';

// Mock authService
jest.mock('../../services/authService', () => ({
  authService: {
    login: jest.fn(),
    loginByCode: jest.fn(),
    register: jest.fn(),
    wechatLogin: jest.fn(),
    updateUser: jest.fn(),
  },
}));

// Mock localStorage
const localStorageMock = {
  getItem: jest.fn(),
  setItem: jest.fn(),
  removeItem: jest.fn(),
  clear: jest.fn(),
};
Object.defineProperty(window, 'localStorage', {
  value: localStorageMock,
});

describe('authStore', () => {
  beforeEach(() => {
    localStorageMock.getItem.mockClear();
    localStorageMock.setItem.mockClear();
    localStorageMock.removeItem.mockClear();
    localStorageMock.clear.mockClear();
    
    // Reset store state
    const { result } = renderHook(() => useAuthStore());
    act(() => {
      result.current.logout();
    });
  });

  test('initializes with guest state when no token', () => {
    localStorageMock.getItem.mockReturnValue(null);
    
    const { result } = renderHook(() => useAuthStore());
    
    expect(result.current.isGuest).toBe(true);
    expect(result.current.isLoggedIn).toBe(false);
    expect(result.current.user).toBeNull();
    expect(result.current.accessToken).toBeNull();
  });

  test('initializes with logged in state when token exists', () => {
    const mockUser = { 
      id: '1', 
      phone: '13800000001', 
      nickname: 'Test User',
      avatar_url: '',
      gender: '',
      company: '',
      position: '',
      email: '',
      level: 'newbie',
      credit_score: 0,
      cocoa_beans: 0,
      reputation_points: 0,
      is_guest: false,
      checked_in_today: false,
      early_bird_available: false,
      early_bird_count: 0,
      created_at: new Date().toISOString()
    };
    localStorageMock.getItem
      .mockReturnValueOnce('mock-token') // access_token
      .mockReturnValueOnce(JSON.stringify(mockUser)); // user
    
    const { result } = renderHook(() => useAuthStore());
    
    expect(result.current.isGuest).toBe(false);
    expect(result.current.isLoggedIn).toBe(true);
    expect(result.current.user).toEqual(mockUser);
    expect(result.current.accessToken).toBe('mock-token');
  });

  test('handles invalid user data gracefully', () => {
    localStorageMock.getItem
      .mockReturnValueOnce('mock-token') // access_token
      .mockReturnValueOnce('invalid-json'); // user (invalid JSON)
    
    const { result } = renderHook(() => useAuthStore());
    
    expect(result.current.isGuest).toBe(true);
    expect(result.current.isLoggedIn).toBe(false);
    expect(result.current.user).toBeNull();
  });

  test('sets guest state', () => {
    const { result } = renderHook(() => useAuthStore());
    
    act(() => {
      result.current.setGuest();
    });
    
    expect(result.current.isGuest).toBe(true);
    expect(result.current.isLoggedIn).toBe(false);
  });

  test('logs out user', () => {
    const { result } = renderHook(() => useAuthStore());
    
    // Set some initial state
    act(() => {
      useAuthStore.setState({
        isGuest: false,
        isLoggedIn: true,
        user: { 
          id: '1', 
          phone: '13800000001', 
          nickname: 'Test User',
          avatar_url: '',
          gender: '',
          company: '',
          position: '',
          email: '',
          level: 'newbie',
          credit_score: 0,
          cocoa_beans: 0,
          reputation_points: 0,
          is_guest: false,
          checked_in_today: false,
          early_bird_available: false,
          early_bird_count: 0,
          created_at: new Date().toISOString()
        },
        accessToken: 'mock-token',
      });
    });
    
    act(() => {
      result.current.logout();
    });
    
    expect(result.current.isGuest).toBe(true);
    expect(result.current.isLoggedIn).toBe(false);
    expect(result.current.user).toBeNull();
    expect(result.current.accessToken).toBeNull();
    expect(localStorageMock.removeItem).toHaveBeenCalledWith('access_token');
    expect(localStorageMock.removeItem).toHaveBeenCalledWith('user');
  });
});