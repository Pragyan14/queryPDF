import { create } from 'zustand';
import axios from 'axios';

export const useQsStore = create((set) => ({
    uploadedFileId: null,
    uploadedFileName: null,
    isUploading: false,
    isLoading: false,
    error: null,
    messages: [],

    uploadPdf: async (file) => {
        set(({ isUploading: true, error: null }))
        try {
            const formData = new FormData();
            formData.append('file', file);
            const res = await axios.post('http://localhost:8000/upload-pdf', formData);
            set({ uploadedFileId: res.data.pdf_id, uploadedFileName: file.name, isUploading: false });
            return true
        } catch (err) {
            const message = err.response.data.detail || 'Upload failed'
            set({ error: message, isUploading: false });
            return false
        }
    },

    askQuestion: async (question) => {
        const { uploadedFileId } = useQsStore.getState()
        const userMessage = {
            id: Date.now().toString(),
            type: 'user',
            content: question,
            timestamp: new Date(),
        }
        const typingMessageId = (Date.now()+1).toString();
        const typingMessage = {
            id: typingMessageId,
            type: 'bot',
            content: "Thinking...",
            timestamp: new Date(),
        }
        set((state) => ({
            isLoading: true,
            error: null,
            messages: [...state.messages,userMessage,typingMessage]
        }))

        try {
            const res = await axios.post("http://localhost:8000/ask-question", { pdf_id: uploadedFileId, question });
            set((state) => ({
                isLoading: false,
                messages: state.messages.map((msg) => {
                    return msg.id === typingMessageId
                    ?{
                        ...msg,
                        content:res.data.answer,
                        timestamp:new Date()
                    }
                    :msg
                })
            }))
            return true
        } catch (err) {
            set((state) => ({ 
                isLoading: false,
                messages: state.messages.map((msg) => {
                    return msg.id === typingMessageId
                    ?{
                        ...msg,
                        content:"Error getting answer",
                        timestamp:new Date()
                    }
                    :msg
                }),
                error: "Error getting answer"
             }));
            return false
        }
    }
}))