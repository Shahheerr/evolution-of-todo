"use client";

import { useState, useEffect, useCallback } from "react";
import { useRouter } from "next/navigation";
import { useSession, signOut } from "@/lib/auth-client";
import { taskApi, Task, TaskFilters, Priority, Status, CreateTaskInput, UpdateTaskInput } from "@/lib/api";
import { AIChat } from "@/components/AIChat";

// =============================================================================
// Task Form Modal Component
// =============================================================================

interface TaskFormProps {
    task?: Task | null;
    onSubmit: (data: CreateTaskInput | UpdateTaskInput) => Promise<void>;
    onClose: () => void;
    loading: boolean;
}

function TaskFormModal({ task, onSubmit, onClose, loading }: TaskFormProps) {
    const [title, setTitle] = useState(task?.title || "");
    const [description, setDescription] = useState(task?.description || "");
    const [priority, setPriority] = useState<Priority>(task?.priority || "MEDIUM");
    const [status, setStatus] = useState<Status>(task?.status || "PENDING");
    const [dueDate, setDueDate] = useState(task?.dueDate?.slice(0, 10) || "");
    const [tagsInput, setTagsInput] = useState(task?.tags?.join(", ") || "");

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        const tags = tagsInput.split(",").map(t => t.trim()).filter(Boolean);
        await onSubmit({
            title,
            description: description || undefined,
            priority,
            status,
            dueDate: dueDate || undefined,
            tags,
        });
    };

    return (
        <div className="modal-overlay" onClick={onClose}>
            <div className="modal" onClick={e => e.stopPropagation()}>
                <div className="modal-header">
                    <h2 className="modal-title">{task ? "Edit Task" : "Create New Task"}</h2>
                    <button className="btn btn-ghost btn-sm" onClick={onClose}>✕</button>
                </div>

                <form onSubmit={handleSubmit}>
                    <div className="form-group">
                        <label className="label">Title *</label>
                        <input
                            type="text"
                            className="input"
                            value={title}
                            onChange={e => setTitle(e.target.value)}
                            placeholder="What needs to be done?"
                            required
                            disabled={loading}
                        />
                    </div>

                    <div className="form-group">
                        <label className="label">Description</label>
                        <textarea
                            className="input"
                            value={description}
                            onChange={e => setDescription(e.target.value)}
                            placeholder="Add more details..."
                            rows={3}
                            disabled={loading}
                            style={{ resize: "vertical" }}
                        />
                    </div>

                    <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "1rem" }}>
                        <div className="form-group">
                            <label className="label">Priority</label>
                            <select
                                className="input select"
                                value={priority}
                                onChange={e => setPriority(e.target.value as Priority)}
                                disabled={loading}
                            >
                                <option value="HIGH">🔴 High</option>
                                <option value="MEDIUM">🟡 Medium</option>
                                <option value="LOW">🟢 Low</option>
                            </select>
                        </div>

                        <div className="form-group">
                            <label className="label">Status</label>
                            <select
                                className="input select"
                                value={status}
                                onChange={e => setStatus(e.target.value as Status)}
                                disabled={loading}
                            >
                                <option value="PENDING">📋 Pending</option>
                                <option value="IN_PROGRESS">🔄 In Progress</option>
                                <option value="COMPLETED">✅ Completed</option>
                            </select>
                        </div>
                    </div>

                    <div className="form-group">
                        <label className="label">Due Date</label>
                        <input
                            type="date"
                            className="input"
                            value={dueDate}
                            onChange={e => setDueDate(e.target.value)}
                            disabled={loading}
                        />
                    </div>

                    <div className="form-group">
                        <label className="label">Tags (comma-separated)</label>
                        <input
                            type="text"
                            className="input"
                            value={tagsInput}
                            onChange={e => setTagsInput(e.target.value)}
                            placeholder="Work, Personal, Urgent"
                            disabled={loading}
                        />
                    </div>

                    <div className="flex gap-md" style={{ marginTop: "1.5rem" }}>
                        <button type="button" className="btn btn-secondary" onClick={onClose} disabled={loading}>
                            Cancel
                        </button>
                        <button type="submit" className="btn btn-primary" disabled={loading} style={{ flex: 1 }}>
                            {loading ? "Saving..." : task ? "Update Task" : "Create Task"}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
}

// =============================================================================
// Task Card Component
// =============================================================================

interface TaskCardProps {
    task: Task;
    onEdit: (task: Task) => void;
    onDelete: (taskId: string) => void;
    onStatusChange: (taskId: string, status: Status) => void;
}

function TaskCard({ task, onEdit, onDelete, onStatusChange }: TaskCardProps) {
    const priorityColors: Record<Priority, string> = {
        HIGH: "badge-priority-high",
        MEDIUM: "badge-priority-medium",
        LOW: "badge-priority-low",
    };

    const statusColors: Record<Status, string> = {
        PENDING: "badge-status-pending",
        IN_PROGRESS: "badge-status-in-progress",
        COMPLETED: "badge-status-completed",
    };

    const isCompleted = task.status === "COMPLETED";

    return (
        <div className="card" style={{
            opacity: isCompleted ? 0.7 : 1,
            transition: "all 0.2s ease",
        }}>
            <div className="flex items-center gap-md" style={{ marginBottom: "0.75rem" }}>
                {/* Checkbox */}
                <div
                    className={`checkbox ${isCompleted ? "checked" : ""}`}
                    onClick={() => onStatusChange(task.id, isCompleted ? "PENDING" : "COMPLETED")}
                />

                {/* Title */}
                <h3 style={{
                    flex: 1,
                    fontSize: "1rem",
                    textDecoration: isCompleted ? "line-through" : "none",
                    color: isCompleted ? "#64748b" : "#f8fafc",
                }}>
                    {task.title}
                </h3>

                {/* Actions */}
                <div className="flex gap-sm">
                    <button className="btn btn-ghost btn-sm" onClick={() => onEdit(task)}>
                        ✏️
                    </button>
                    <button className="btn btn-ghost btn-sm" onClick={() => onDelete(task.id)}>
                        🗑️
                    </button>
                </div>
            </div>

            {/* Description */}
            {task.description && (
                <p style={{
                    fontSize: "0.875rem",
                    color: "#94a3b8",
                    marginBottom: "0.75rem",
                    marginLeft: "2rem",
                }}>
                    {task.description}
                </p>
            )}

            {/* Meta */}
            <div className="flex items-center gap-sm" style={{ marginLeft: "2rem", flexWrap: "wrap" }}>
                <span className={`badge ${priorityColors[task.priority]}`}>
                    {task.priority}
                </span>
                <span className={`badge ${statusColors[task.status]}`}>
                    {task.status.replace("_", " ")}
                </span>
                {task.dueDate && (
                    <span className="tag">
                        📅 {new Date(task.dueDate).toLocaleDateString()}
                    </span>
                )}
                {task.tags.map((tag, i) => (
                    <span key={i} className="tag">#{tag}</span>
                ))}
            </div>
        </div>
    );
}

// =============================================================================
// Main Dashboard Component
// =============================================================================

export default function DashboardPage() {
    const { data: session, isPending } = useSession();
    const router = useRouter();

    // Task state
    const [tasks, setTasks] = useState<Task[]>([]);
    const [totalTasks, setTotalTasks] = useState(0);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");

    // Filter state
    const [search, setSearch] = useState("");
    const [statusFilter, setStatusFilter] = useState<Status | "">("");
    const [priorityFilter, setPriorityFilter] = useState<Priority | "">("");
    const [sortBy, setSortBy] = useState<TaskFilters["sortBy"]>("createdAt");
    const [sortOrder, setSortOrder] = useState<TaskFilters["sortOrder"]>("desc");

    // Modal state
    const [showModal, setShowModal] = useState(false);
    const [editingTask, setEditingTask] = useState<Task | null>(null);
    const [formLoading, setFormLoading] = useState(false);

    // AI Chat state
    const [showAIChat, setShowAIChat] = useState(false);

    // Redirect if not authenticated
    useEffect(() => {
        if (!isPending && !session) {
            router.push("/auth/login");
        }
    }, [session, isPending, router]);

    // Fetch tasks
    const fetchTasks = useCallback(async () => {
        try {
            setLoading(true);
            setError("");

            const filters: TaskFilters = {
                search: search || undefined,
                status: statusFilter || undefined,
                priority: priorityFilter || undefined,
                sortBy,
                sortOrder,
                pageSize: 50,
            };

            const response = await taskApi.list(filters);
            setTasks(response.tasks);
            setTotalTasks(response.total);
        } catch (err) {
            console.error("Error fetching tasks:", err);
            setError(err instanceof Error ? err.message : "Failed to load tasks");
        } finally {
            setLoading(false);
        }
    }, [search, statusFilter, priorityFilter, sortBy, sortOrder]);

    useEffect(() => {
        if (session) {
            fetchTasks();
        }
    }, [session, fetchTasks]);

    // Handlers
    const handleCreateTask = async (data: CreateTaskInput) => {
        try {
            setFormLoading(true);
            await taskApi.create(data);
            setShowModal(false);
            fetchTasks();
        } catch (err) {
            alert(err instanceof Error ? err.message : "Failed to create task");
        } finally {
            setFormLoading(false);
        }
    };

    const handleUpdateTask = async (data: UpdateTaskInput) => {
        if (!editingTask) return;
        try {
            setFormLoading(true);
            await taskApi.update(editingTask.id, data);
            setShowModal(false);
            setEditingTask(null);
            fetchTasks();
        } catch (err) {
            alert(err instanceof Error ? err.message : "Failed to update task");
        } finally {
            setFormLoading(false);
        }
    };

    const handleDeleteTask = async (taskId: string) => {
        if (!confirm("Are you sure you want to delete this task?")) return;
        try {
            await taskApi.delete(taskId);
            fetchTasks();
        } catch (err) {
            alert(err instanceof Error ? err.message : "Failed to delete task");
        }
    };

    const handleStatusChange = async (taskId: string, status: Status) => {
        try {
            await taskApi.updateStatus(taskId, status);
            fetchTasks();
        } catch (err) {
            alert(err instanceof Error ? err.message : "Failed to update status");
        }
    };

    const handleSignOut = async () => {
        await signOut();
        router.push("/");
    };

    // Loading state
    if (isPending) {
        return (
            <div className="loading-overlay" style={{ minHeight: "100vh" }}>
                <div className="spinner"></div>
            </div>
        );
    }

    if (!session) {
        return null;
    }

    // Stats
    const completedCount = tasks.filter(t => t.status === "COMPLETED").length;
    const pendingCount = tasks.filter(t => t.status === "PENDING").length;
    const inProgressCount = tasks.filter(t => t.status === "IN_PROGRESS").length;

    return (
        <div style={{ minHeight: "100vh" }}>
            {/* Header */}
            <header style={{
                borderBottom: "1px solid var(--color-border)",
                padding: "1rem 2rem",
                background: "rgba(30, 30, 63, 0.5)",
                backdropFilter: "blur(10px)",
                position: "sticky",
                top: 0,
                zIndex: 50,
            }}>
                <div className="container flex items-center justify-between">
                    <div style={{
                        fontSize: "1.25rem",
                        fontWeight: "700",
                        background: "linear-gradient(135deg, #6366f1, #8b5cf6)",
                        WebkitBackgroundClip: "text",
                        WebkitTextFillColor: "transparent",
                    }}>
                        ✨ TaskFlow
                    </div>

                    <div className="flex items-center gap-md">
                        <span style={{ color: "#94a3b8", fontSize: "0.875rem" }}>
                            👋 {session.user.name || session.user.email}
                        </span>
                        <button className="btn btn-ghost btn-sm" onClick={handleSignOut}>
                            Sign Out
                        </button>
                    </div>
                </div>
            </header>

            {/* Main Content with AI Chat */}
            <main className="container" style={{ padding: "2rem" }}>
                <div className="dashboard-with-chat">
                    {/* Task Management Section */}
                    <div className="dashboard-main">
                        {/* Page Title & Stats */}
                        <div className="flex items-center justify-between" style={{ marginBottom: "2rem" }}>
                            <div>
                                <h1 style={{ fontSize: "2rem", marginBottom: "0.5rem" }}>
                                    My Tasks
                                    <span style={{
                                        fontSize: "0.75rem",
                                        marginLeft: "0.5rem",
                                        background: "linear-gradient(135deg, #6366f1, #8b5cf6)",
                                        padding: "2px 8px",
                                        borderRadius: "9999px",
                                        color: "white",
                                        verticalAlign: "middle"
                                    }}>
                                        🤖 AI Powered
                                    </span>
                                </h1>
                                <p style={{ color: "#94a3b8" }}>
                                    {totalTasks} total • {completedCount} completed • {pendingCount} pending • {inProgressCount} in progress
                                </p>
                            </div>
                            <button
                                className="btn btn-primary"
                                onClick={() => { setEditingTask(null); setShowModal(true); }}
                            >
                                ➕ New Task
                            </button>
                        </div>

                        {/* Filters */}
                        <div className="card" style={{ marginBottom: "1.5rem" }}>
                            <div style={{
                                display: "grid",
                                gridTemplateColumns: "repeat(auto-fit, minmax(150px, 1fr))",
                                gap: "1rem",
                            }}>
                                {/* Search */}
                                <div>
                                    <label className="label">Search</label>
                                    <input
                                        type="text"
                                        className="input"
                                        placeholder="Search tasks..."
                                        value={search}
                                        onChange={e => setSearch(e.target.value)}
                                    />
                                </div>

                                {/* Status Filter */}
                                <div>
                                    <label className="label">Status</label>
                                    <select
                                        className="input select"
                                        value={statusFilter}
                                        onChange={e => setStatusFilter(e.target.value as Status | "")}
                                    >
                                        <option value="">All Status</option>
                                        <option value="PENDING">Pending</option>
                                        <option value="IN_PROGRESS">In Progress</option>
                                        <option value="COMPLETED">Completed</option>
                                    </select>
                                </div>

                                {/* Priority Filter */}
                                <div>
                                    <label className="label">Priority</label>
                                    <select
                                        className="input select"
                                        value={priorityFilter}
                                        onChange={e => setPriorityFilter(e.target.value as Priority | "")}
                                    >
                                        <option value="">All Priorities</option>
                                        <option value="HIGH">High</option>
                                        <option value="MEDIUM">Medium</option>
                                        <option value="LOW">Low</option>
                                    </select>
                                </div>

                                {/* Sort By */}
                                <div>
                                    <label className="label">Sort By</label>
                                    <select
                                        className="input select"
                                        value={sortBy}
                                        onChange={e => setSortBy(e.target.value as TaskFilters["sortBy"])}
                                    >
                                        <option value="createdAt">Date Created</option>
                                        <option value="dueDate">Due Date</option>
                                        <option value="priority">Priority</option>
                                        <option value="title">Title</option>
                                    </select>
                                </div>

                                {/* Sort Order */}
                                <div>
                                    <label className="label">Order</label>
                                    <select
                                        className="input select"
                                        value={sortOrder}
                                        onChange={e => setSortOrder(e.target.value as TaskFilters["sortOrder"])}
                                    >
                                        <option value="desc">Newest First</option>
                                        <option value="asc">Oldest First</option>
                                    </select>
                                </div>
                            </div>
                        </div>

                        {/* Error State */}
                        {error && (
                            <div className="alert alert-error">{error}</div>
                        )}

                        {/* Loading State */}
                        {loading ? (
                            <div className="loading-overlay">
                                <div className="spinner"></div>
                            </div>
                        ) : tasks.length === 0 ? (
                            /* Empty State */
                            <div className="empty-state">
                                <div className="empty-state-icon">📝</div>
                                <h3 style={{ marginBottom: "0.5rem" }}>No tasks yet</h3>
                                <p>Create your first task or ask the AI assistant!</p>
                                <button
                                    className="btn btn-primary"
                                    style={{ marginTop: "1rem" }}
                                    onClick={() => { setEditingTask(null); setShowModal(true); }}
                                >
                                    ➕ Create Task
                                </button>
                            </div>
                        ) : (
                            /* Task List */
                            <div className="flex flex-col gap-md">
                                {tasks.map(task => (
                                    <TaskCard
                                        key={task.id}
                                        task={task}
                                        onEdit={(t) => { setEditingTask(t); setShowModal(true); }}
                                        onDelete={handleDeleteTask}
                                        onStatusChange={handleStatusChange}
                                    />
                                ))}
                            </div>
                        )}
                    </div>

                    {/* AI Chat Section - Desktop */}
                    <div className={`dashboard-chat ${showAIChat ? 'open' : ''}`}>
                        <AIChat onTasksUpdated={fetchTasks} />
                    </div>
                </div>

                {/* AI Chat Toggle Button - Mobile/Tablet */}
                <button
                    className="ai-chat-toggle"
                    onClick={() => setShowAIChat(!showAIChat)}
                    aria-label="Toggle AI Chat"
                >
                    {showAIChat ? '✕' : '🤖'}
                </button>
            </main>

            {/* Modal */}
            {showModal && (
                <TaskFormModal
                    task={editingTask}
                    onSubmit={editingTask ? handleUpdateTask : handleCreateTask}
                    onClose={() => { setShowModal(false); setEditingTask(null); }}
                    loading={formLoading}
                />
            )}
        </div>
    );
}
