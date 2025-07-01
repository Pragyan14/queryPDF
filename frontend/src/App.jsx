import { useState } from 'react';
import { Send, FileText, User, Bot, CirclePlus, SendHorizontal, Loader } from "lucide-react"
import { Button } from "../src/components/ui/Button"
import { Input } from "../src/components/ui/Input"
import { useQsStore } from './store/qaStore';
import toast, { Toaster } from 'react-hot-toast';

function App() {

  const { messages, error, isUploading, uploadedFileId, uploadedFileName, uploadPdf, askQuestion } = useQsStore()

  const [inputMessage, setInputMessage] = useState("");

  const handleSendMessage = async () => {
    const question = inputMessage.trim();
    if(!question) return;
    setInputMessage("")
    await askQuestion(question);
  }

  const handleKeyPress = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault()
      handleSendMessage()
    }
  }
  const handleFileChange = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;
    if (file.size > 2 * 1024 * 1024) {
      toast.error("File size must be less than 2MB");
      return;
    }
    const success = await uploadPdf(file);
    if (success) {
      toast.success("File uploaded successfully");
    } else {
      toast.error(error || "File upload failed");
    }
  }

  return (
    <>
      <Toaster />
      <div className='flex flex-col h-screen bg-gray-50'>
        <header className="bg-white border-b border-gray-200 px-4 sm:px-8 md:px-12 py-3 flex flex-wrap items-center justify-between gap-4">
          {/* Logo */}
          <div className="flex items-center w-24 h-10 sm:h-12">
            <img src="logo.png" alt="logo" className="h-full object-contain" />
          </div>

          {/* Actions: Uploaded file + Upload button */}
          <div className="flex flex-wrap items-center gap-2">
            {uploadedFileId && (
              <div className="flex items-center gap-1 text-sm text-[#0FA958] bg-gray-100 px-2 py-1 rounded">
                <FileText className="w-4 h-4" />
                <span >{uploadedFileName}</span>
              </div>
            )}

            <input
              type="file"
              id="pdfUpload"
              accept="application/pdf"
              className="hidden"
              onChange={handleFileChange}
              disabled={uploadedFileId}
            />
            <label
              htmlFor='pdfUpload'
              className={`flex items-center gap-2 border border-black px-4 py-2 sm:px-5 sm:py-1.5 rounded-md cursor-pointer transition-colors duration-200 text-sm sm:text-base ${uploadedFileId || isUploading
                ? "bg-gray-300 text-gray-600 cursor-not-allowed"
                : "hover:bg-black hover:text-white"
                }`}
            >
              <CirclePlus className="w-4 h-4" />
              <span className="hidden sm:inline font-semibold">Upload PDF</span>
            </label>
          </div>
        </header>

        {/* Chat Area */}
        <div className="flex-1 flex flex-col max-w-4xl mx-auto w-full overflow-hidden">
          {/* Messages Container */}
          <div className="flex-1 overflow-y-auto p-4 space-y-4">
            {messages.length === 0 ? (
              <>
                <div className="flex-1 flex items-center justify-center">
                  <div className="text-center text-gray-500">
                    <FileText className="w-12 h-12 mx-auto mb-4 text-gray-300" />
                    <p className="text-lg mb-2">Upload a PDF to get started</p>
                    <p className="text-sm">Ask questions about your document and get instant answers</p>
                  </div>
                </div>

              </>

            ) : (
              <div className="space-y-4">
                {messages.map((message) => (
                  <div
                    key={message.id}
                    className={`flex items-start space-x-3 ${message.type === "user" ? "justify-end" : "justify-start"}`}
                  >
                    {message.type === "bot" && (
                      <div className="w-8 h-8 bg-green-500 rounded-full flex items-center justify-center flex-shrink-0">
                        <Bot className="w-4 h-4 text-white" />
                      </div>
                    )}

                    <div
                      className={`max-w-xs sm:max-w-md lg:max-w-lg xl:max-w-xl px-4 py-2 rounded-lg ${message.type === "user"
                        ? "bg-blue-500 text-white"
                        : "bg-white border border-gray-200 text-gray-800"
                        }`}
                    >
                      <p className="text-sm leading-relaxed">{message.content}</p>
                    </div>

                    {message.type === "user" && (
                      <div className="w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center flex-shrink-0">
                        <User className="w-4 h-4 text-white" />
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Input Area */}
          <div className="border-t border-gray-200 bg-white p-4">
            {!isUploading ? (
              <div className="flex items-center space-x-2 max-w-4xl mx-auto">
                <div className="flex-1 relative">
                  <Input
                    value={inputMessage}
                    onChange={(e) => setInputMessage(e.target.value)}
                    onKeyPress={handleKeyPress}
                    disabled={!uploadedFileId}
                    placeholder="Send a message..."
                    className="pr-12 py-3 text-sm border-gray-300 focus:border-blue-500 focus:ring-blue-500"
                  />
                  <Button
                    onClick={handleSendMessage}
                    size="sm"
                    disabled={!uploadedFileId}
                    className="absolute right-2 top-1/2 transform -translate-y-1/2 h-8 w-8"
                  >
                    <SendHorizontal className="w-5 h-5" />
                  </Button>
                </div>
              </div>
            ) : (
              <Loader className='mx-auto animate-spin' size={"42"} />
            )}
          </div>


        </div>

      </div>
    </>
  )
}

export default App
