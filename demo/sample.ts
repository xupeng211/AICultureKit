/**
 * 演示TypeScript文件 - 用于测试多语言分析功能
 */

// TypeScript接口定义
interface User {
    id: number;
    firstName: string;
    lastName: string;
    email: string;
    age: number;
    role: UserRole;
    isActive: boolean;
    createdAt: string;
}

// 枚举类型
enum UserRole {
    ADMIN = 'admin',
    EDITOR = 'editor',
    VIEWER = 'viewer',
    GUEST = 'guest'
}

// 泛型接口
interface ApiResponse<T> {
    data: T;
    status: number;
    message: string;
}

// 类型别名
type UserFilter = {
    activeOnly?: boolean;
    minAge?: number;
    roles?: UserRole[];
    sortBy?: 'name' | 'age' | 'id';
};

// TypeScript类
class TypedUserService {
    private readonly apiUrl: string;
    private users: User[] = [];
    private isLoading: boolean = false;

    constructor(apiUrl: string) {
        this.apiUrl = apiUrl;
    }

    // 泛型方法
    async fetchData<T>(endpoint: string): Promise<ApiResponse<T>> {
        const response = await fetch(`${this.apiUrl}${endpoint}`);

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        return response.json() as Promise<ApiResponse<T>>;
    }

    // 类型安全的用户获取
    async getUsers(): Promise<User[]> {
        if (this.isLoading) {
            return this.users;
        }

        this.isLoading = true;

        try {
            const response = await this.fetchData<User[]>('/users');
            this.users = response.data;
            return this.users;
        } finally {
            this.isLoading = false;
        }
    }

    // 可选参数和联合类型
    findUser(criteria: number | string | Partial<User>): User | undefined {
        if (typeof criteria === 'number') {
            return this.users.find(user => user.id === criteria);
        }

        if (typeof criteria === 'string') {
            return this.users.find(user =>
                user.email === criteria ||
                user.firstName === criteria ||
                user.lastName === criteria
            );
        }

        return this.users.find(user => {
            return Object.keys(criteria).every(key =>
                user[key as keyof User] === criteria[key as keyof User]
            );
        });
    }

    // 函数重载
    filterUsers(filter: UserFilter): User[];
    filterUsers(predicate: (user: User) => boolean): User[];
    filterUsers(filterOrPredicate: UserFilter | ((user: User) => boolean)): User[] {
        if (typeof filterOrPredicate === 'function') {
            return this.users.filter(filterOrPredicate);
        }

        const filter = filterOrPredicate;
        return this.users.filter(user => {
            if (filter.activeOnly && !user.isActive) {
                return false;
            }

            if (filter.minAge && user.age < filter.minAge) {
                return false;
            }

            if (filter.roles && !filter.roles.includes(user.role)) {
                return false;
            }

            return true;
        });
    }

    // 私有方法
    private validateUser(user: Partial<User>): user is User {
        return !!(
            user.id &&
            user.firstName &&
            user.lastName &&
            user.email &&
            user.age &&
            user.role &&
            typeof user.isActive === 'boolean'
        );
    }
}

// 高阶函数和泛型
function createAsyncCache<K, V>(
    fetcher: (key: K) => Promise<V>,
    ttl: number = 5 * 60 * 1000 // 5分钟默认TTL
) {
    const cache = new Map<K, { value: V; expiry: number }>();

    return async (key: K): Promise<V> => {
        const cached = cache.get(key);
        const now = Date.now();

        if (cached && cached.expiry > now) {
            return cached.value;
        }

        const value = await fetcher(key);
        cache.set(key, { value, expiry: now + ttl });

        return value;
    };
}

// 装饰器（如果启用实验性装饰器）
function measure(target: any, propertyName: string, descriptor: PropertyDescriptor) {
    const method = descriptor.value;

    descriptor.value = function (...args: any[]) {
        const start = performance.now();
        const result = method.apply(this, args);
        const end = performance.now();
        console.log(`${propertyName} took ${end - start} milliseconds`);
        return result;
    };
}

// 类型守卫
function isUser(obj: any): obj is User {
    return obj &&
        typeof obj.id === 'number' &&
        typeof obj.firstName === 'string' &&
        typeof obj.lastName === 'string' &&
        typeof obj.email === 'string' &&
        typeof obj.age === 'number' &&
        Object.values(UserRole).includes(obj.role) &&
        typeof obj.isActive === 'boolean';
}

// 工具类型使用
type UserUpdate = Partial<Pick<User, 'firstName' | 'lastName' | 'email' | 'role'>>;
type UserSummary = Omit<User, 'createdAt'> & { displayName: string };

// 条件类型
type NonNullable<T> = T extends null | undefined ? never : T;

// 映射类型
type ReadonlyUser = {
    readonly [K in keyof User]: User[K];
};

// 导出
export {
    User,
    UserRole,
    ApiResponse,
    UserFilter,
    TypedUserService,
    createAsyncCache,
    isUser,
    UserUpdate,
    UserSummary
};

export default TypedUserService;
