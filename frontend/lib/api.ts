/**
 * API Client for communicating with FastAPI backend.
 * 
 * This module handles:
 * - JWT token attachment to all requests
 * - Type-safe API methods for Task CRUD
 * - Error handling
 */

import { getJwtToken } from "./auth-client";

// API base URL
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api";

// =============================================================================
// Types
// =============================================================================

export type Priority = "HIGH" | "MEDIUM" | "LOW";
export type Status = "PENDING" | "IN_PROGRESS" | "COMPLETED";

export interface Task {
    id: string;
    title: string;
    description: string | null;
    status: Status;
    priority: Priority;
    dueDate: string | null;
    tags: string[];
    createdAt: string;
    updatedAt: string;
    userId: string;
}

export interface TaskListResponse {
    tasks: Task[];
    total: number;
    page: number;
    pageSize: number;
    totalPages: number;
}

export interface CreateTaskInput {
    title: string;
    description?: string;
    status?: Status;
    priority?: Priority;
    dueDate?: string;
    tags?: string[];
}

export interface UpdateTaskInput {
    title?: string;
    description?: string;
    status?: Status;
    priority?: Priority;
    dueDate?: string;
    tags?: string[];
}

export interface TaskFilters {
    search?: string;
    status?: Status;
    priority?: Priority;
    tag?: string;
    sortBy?: "createdAt" | "dueDate" | "priority" | "title";
    sortOrder?: "asc" | "desc";
    page?: number;
    pageSize?: number;
}

// =============================================================================
// API Error Class
// =============================================================================

export class ApiError extends Error {
    constructor(
        message: string,
        public status: number,
        public details?: unknown
    ) {
        super(message);
        this.name = "ApiError";
    }
}

// =============================================================================
// API Request Helper
// =============================================================================

async function apiRequest<T>(
    endpoint: string,
    options: RequestInit = {}
): Promise<T> {
    // Get JWT token
    const token = await getJwtToken();

    if (!token) {
        throw new ApiError("Not authenticated. Please log in.", 401);
    }

    const url = `${API_BASE_URL}${endpoint}`;

    const response = await fetch(url, {
        ...options,
        headers: {
            "Content-Type": "application/json",
            "Authorization": `Bearer ${token}`,
            ...options.headers,
        },
    });

    if (!response.ok) {
        let errorMessage = "An error occurred";
        try {
            const errorData = await response.json();
            errorMessage = errorData.detail || errorData.message || errorMessage;
        } catch {
            errorMessage = response.statusText;
        }
        throw new ApiError(errorMessage, response.status);
    }

    // Handle 204 No Content
    if (response.status === 204) {
        return undefined as T;
    }

    return response.json();
}

// =============================================================================
// Task API Methods
// =============================================================================

export const taskApi = {
    /**
     * Get all tasks with optional filters
     */
    async list(filters: TaskFilters = {}): Promise<TaskListResponse> {
        const params = new URLSearchParams();

        if (filters.search) params.append("search", filters.search);
        if (filters.status) params.append("status", filters.status);
        if (filters.priority) params.append("priority", filters.priority);
        if (filters.tag) params.append("tag", filters.tag);
        if (filters.sortBy) params.append("sortBy", filters.sortBy);
        if (filters.sortOrder) params.append("sortOrder", filters.sortOrder);
        if (filters.page) params.append("page", filters.page.toString());
        if (filters.pageSize) params.append("pageSize", filters.pageSize.toString());

        const queryString = params.toString();
        const endpoint = `/tasks${queryString ? `?${queryString}` : ""}`;

        return apiRequest<TaskListResponse>(endpoint);
    },

    /**
     * Get a single task by ID
     */
    async get(taskId: string): Promise<Task> {
        return apiRequest<Task>(`/tasks/${taskId}`);
    },

    /**
     * Create a new task
     */
    async create(data: CreateTaskInput): Promise<Task> {
        return apiRequest<Task>("/tasks", {
            method: "POST",
            body: JSON.stringify(data),
        });
    },

    /**
     * Update an existing task
     */
    async update(taskId: string, data: UpdateTaskInput): Promise<Task> {
        return apiRequest<Task>(`/tasks/${taskId}`, {
            method: "PUT",
            body: JSON.stringify(data),
        });
    },

    /**
     * Update task status (mark complete/incomplete)
     */
    async updateStatus(taskId: string, status: Status): Promise<Task> {
        return apiRequest<Task>(`/tasks/${taskId}/status`, {
            method: "PATCH",
            body: JSON.stringify({ status }),
        });
    },

    /**
     * Delete a task
     */
    async delete(taskId: string): Promise<void> {
        return apiRequest<void>(`/tasks/${taskId}`, {
            method: "DELETE",
        });
    },

    /**
     * Delete all completed tasks
     */
    async deleteCompleted(): Promise<void> {
        return apiRequest<void>("/tasks", {
            method: "DELETE",
        });
    },
};
