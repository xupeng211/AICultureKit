/**
 * 演示JavaScript文件 - 用于测试多语言分析功能
 */

// ES6 模块导入
import { utils, config } from './utils.js';
import axios from 'axios';

// 类定义
class UserManager {
    constructor(apiUrl) {
        this.apiUrl = apiUrl;
        this.users = [];
        this.isLoading = false;
    }

    // 异步方法
    async fetchUsers() {
        if (this.isLoading) {
            return;
        }

        this.isLoading = true;

        try {
            const response = await axios.get(`${this.apiUrl}/users`);
            this.users = response.data;
            return this.users;
        } catch (error) {
            console.error('Failed to fetch users:', error);
            throw error;
        } finally {
            this.isLoading = false;
        }
    }

    // 箭头函数
    getUserById = (userId) => {
        return this.users.find(user => user.id === userId);
    }

    // 复杂度较高的函数
    processUserData(userData, options = {}) {
        if (!userData || !Array.isArray(userData)) {
            return [];
        }

        return userData
            .filter(user => {
                if (options.activeOnly && !user.isActive) {
                    return false;
                }
                if (options.minAge && user.age < options.minAge) {
                    return false;
                }
                if (options.roles && !options.roles.includes(user.role)) {
                    return false;
                }
                return true;
            })
            .map(user => ({
                ...user,
                displayName: user.firstName + ' ' + user.lastName,
                isEligible: user.age >= 18 && user.isActive,
                permissions: this.calculatePermissions(user.role)
            }))
            .sort((a, b) => {
                if (options.sortBy === 'name') {
                    return a.displayName.localeCompare(b.displayName);
                } else if (options.sortBy === 'age') {
                    return b.age - a.age;
                } else {
                    return a.id - b.id;
                }
            });
    }

    calculatePermissions(userRole) {
        const permissions = [];

        switch (userRole) {
            case 'admin':
                permissions.push('read', 'write', 'delete', 'manage');
                break;
            case 'editor':
                permissions.push('read', 'write');
                break;
            case 'viewer':
                permissions.push('read');
                break;
            default:
                permissions.push('guest');
        }

        return permissions;
    }
}

// 工具函数
function validateEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

// 使用现代JavaScript特性
const createUser = ({
    firstName,
    lastName,
    email,
    age = 18,
    role = 'viewer',
    ...otherProps
}) => {
    // 解构赋值和模板字符串
    const user = {
        id: Date.now(),
        firstName,
        lastName,
        email: email.toLowerCase(),
        age,
        role,
        isActive: true,
        createdAt: new Date().toISOString(),
        ...otherProps
    };

    // 验证
    if (!validateEmail(user.email)) {
        throw new Error(`Invalid email: ${user.email}`);
    }

    return user;
};

// 异步操作
const initializeApp = async () => {
    try {
        const config = await import('./config.js');
        const userManager = new UserManager(config.API_URL);

        // 获取用户数据
        const users = await userManager.fetchUsers();
        console.log(`Loaded ${users.length} users`);

        return userManager;
    } catch (error) {
        console.error('Failed to initialize app:', error);
        throw error;
    }
};

// 导出
export {
    UserManager,
    createUser,
    validateEmail,
    initializeApp
};

export default UserManager;
