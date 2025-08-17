const getBaseUrl = () => {
    return import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
};

export const apiClient = {
    async get(path: string) {
        const response = await fetch(`${getBaseUrl()}${path}`, {
            headers: {
                'Content-Type': 'application/json',
            },
        });
        if (!response.ok) {
            throw new Error(response.statusText);
        }
        return response.json();
    },

    async post(path: string, body: any) {
        const response = await fetch(`${getBaseUrl()}${path}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(body),
        });
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({ detail: response.statusText }));
            throw new Error(errorData.detail || 'An error occurred');
        }
        return response.json();
    },

    async put(path: string, body: any) {
        const response = await fetch(`${getBaseUrl()}${path}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(body),
        });
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({ detail: response.statusText }));
            throw new Error(errorData.detail || 'An error occurred');
        }
        return response.json();
    },

    async delete(path: string) {
        const response = await fetch(`${getBaseUrl()}${path}`, {
            method: 'DELETE',
        });
        if (!response.ok && response.status !== 204) {
            const errorData = await response.json().catch(() => ({ detail: response.statusText }));
            throw new Error(errorData.detail || 'An error occurred');
        }
        // DELETE might not return a body
        if (response.status === 204) {
            return { success: true };
        }
        return response.json();
    }
};

// Note: This is a very basic client. A real-world app would use a more robust
// solution like axios and handle token refresh, interceptors for error handling, etc.
// For now, this is sufficient to interact with the backend.
