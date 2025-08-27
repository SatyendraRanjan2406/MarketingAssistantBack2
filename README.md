# 🚀 AI Marketing Assistant Chat Integration

This project provides a complete React-based chat interface for the Google Ads Marketing Assistant, with support for campaign creation and various content types.

## ✨ Features

- **Real-time AI Chat**: Interactive conversation with AI marketing assistant
- **Campaign Creation**: Built-in form for creating new Google Ads campaigns
- **Rich Content Support**: Text, tables, lists, actions, charts, and metrics
- **Session Management**: Create, load, and manage chat sessions
- **Responsive Design**: Works on all device sizes
- **TypeScript Support**: Full type safety and IntelliSense

## 🏗️ Project Structure

```
components/
├── AIChatBox.tsx              # Main chat component
└── ChatBlocks/
    ├── CampaignFormBlock.tsx  # Campaign creation form
    ├── TextBlock.tsx          # Text content rendering
    ├── TableBlock.tsx         # Table content rendering
    ├── ListBlock.tsx          # List content rendering
    ├── ActionBlock.tsx        # Action buttons
    ├── ChartBlock.tsx         # Chart visualization
    └── MetricBlock.tsx        # Metric display
```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
npm install
```

### 2. Setup OpenAI Integration (Backend)

```bash
# Install Python dependencies
pip install -r requirements.txt

# Setup OpenAI API key
python setup_openai.py

# Or manually create .env file
cp env_template.txt .env
# Edit .env and add your OpenAI API key
```

### 3. Setup RAG System (Knowledge Base)

Initialize the RAG system with knowledge base:

```bash
python setup_rag_system.py  # Setup and test RAG system
python demo_rag_system.py   # Demo all RAG capabilities
```

**RAG System Features:**
- 🧠 **Smart Context Selection**: Automatically chooses RAG vs Direct OpenAI
- 📚 **Vector Database**: Chroma-based document storage with semantic search
- 🔍 **Intelligent Retrieval**: Context-aware document search and retrieval
- 🔄 **Hybrid Responses**: Combines knowledge base with AI generation
- 📖 **Knowledge Base**: Google Ads best practices and case studies

### 4. Configure Your JWT Token

Update the token in `App.tsx`:

```typescript
const token = 'your-actual-jwt-token-here';
```

### 5. Start the Development Server

```bash
npm start
```

The app will open at `http://localhost:3000`

## 🔧 How It Works

### Campaign Creation Flow

1. **User clicks "Create New Campaign"** button in action block
2. **AI responds with campaign creation form** (CampaignFormBlock)
3. **User fills out the form** with campaign details:
   - Campaign Name (required)
   - Daily Budget (required)
   - Campaign Type (Search, Display, Video, etc.)
   - Initial Status (Paused/Enabled)
4. **Form submits campaign data** to the chat API
5. **AI processes the request** and creates the campaign via Google Ads API
6. **Success message appears** confirming campaign creation

### API Integration

The chat interface integrates with these backend endpoints:

- `POST /api/chat/sessions/create/` - Create new chat session
- `POST /api/chat/message/` - Send message and get AI response
- `GET /api/chat/sessions/` - List user's chat sessions
- `GET /api/chat/sessions/{id}/` - Get chat history
- `DELETE /api/chat/sessions/{id}/delete/` - Delete session

## 🎨 Customization

### Adding New Block Types

1. **Create the block component** in `components/ChatBlocks/`
2. **Add the block type** to the `UIBlock` union in `llm_setup.py`
3. **Update the renderBlock function** in `AIChatBox.tsx`

### Styling

The components use Tailwind CSS classes. You can customize:
- Colors: Update the color classes (e.g., `bg-blue-500`)
- Spacing: Modify padding/margin classes
- Typography: Change font sizes and weights
- Layout: Adjust flexbox and grid classes

## 🔐 Authentication

The chat interface requires a valid JWT token for:
- Creating chat sessions
- Sending messages
- Accessing Google Ads data

Make sure your token is valid and has the necessary permissions.

## 📱 Mobile Support

The interface is fully responsive with:
- Mobile-optimized form inputs
- Touch-friendly buttons
- Responsive message bubbles
- Adaptive chart sizing

## 🐛 Troubleshooting

### Common Issues

1. **"Missing required parameters" Error**
   - The AI is expecting campaign data but none was provided
   - Use the campaign creation form to provide required details

2. **Authentication Errors**
   - Check that your JWT token is valid and not expired
   - Ensure the token has the necessary permissions

3. **API Connection Issues**
   - Verify the backend server is running on `localhost:8000`
   - Check CORS settings if accessing from a different domain

### Debug Mode

Enable console logging to see API requests and responses:

```typescript
// In AIChatBox.tsx
console.log('API Response:', result);
```

## 🚀 Deployment

### Build for Production

```bash
npm run build
```

### Environment Variables

Create a `.env` file for production settings:

```env
REACT_APP_API_BASE_URL=https://your-api-domain.com
REACT_APP_AUTH_TOKEN=your-production-token
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For issues and questions:
1. Check the troubleshooting section above
2. Review the API documentation
3. Check the backend logs for errors
4. Open an issue in the repository

---

**Happy Campaigning! 🎯**
