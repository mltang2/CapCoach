import React, { useState, useRef, useEffect } from 'react';
import { Card } from 'react-bootstrap';

const API_BASE = 'http://localhost:5001/api';

const derivePreferencesFromProfile = (profile) => {
  const protectedCategories = [];
  const profession = (profile?.profession || '').toLowerCase();

  if (profession.includes('dj') || profession.includes('musician') || profession.includes('artist') || profession.includes('producer')) {
    protectedCategories.push('entertainment');
  }
  if (profession.includes('chef') || profession.includes('cook') || profession.includes('food')) {
    protectedCategories.push('dining');
  }
  if (profession.includes('driver') || profession.includes('courier') || profession.includes('uber') || profession.includes('lyft')) {
    protectedCategories.push('transportation');
  }

  return protectedCategories;
};

const derivePreferencesFromText = (text, currentProtected = []) => {
  const protectedSet = new Set(currentProtected);
  const lower = text.toLowerCase();

  const protectSignals = [
    { key: 'entertainment', terms: ['entertainment', 'concert', 'show', 'gig', 'dj', 'music', 'festival', 'movie'] },
    { key: 'dining', terms: ['dining', 'restaurant', 'food', 'eat out', 'takeout', 'delivery'] },
    { key: 'shopping', terms: ['shopping', 'clothes', 'clothing', 'fashion', 'retail', 'buy stuff'] },
    { key: 'transportation', terms: ['car', 'gas', 'transport', 'uber', 'lyft', 'commute'] },
    { key: 'other', terms: ['misc', 'other', 'general', 'personal'] },
  ];

  const cutSignals = [
    { key: 'entertainment', terms: ['cut entertainment', 'less entertainment', 'no shows', 'reduce concerts'] },
    { key: 'dining', terms: ['cut dining', 'less dining', 'cook more', 'no restaurants'] },
    { key: 'shopping', terms: ['cut shopping', 'less shopping', 'no shopping', 'stop buying'] },
    { key: 'transportation', terms: ['cut gas', 'drive less', 'less uber', 'less lyft'] },
  ];

  protectSignals.forEach(({ key, terms }) => {
    if (terms.some((t) => lower.includes(t))) {
      protectedSet.add(key);
    }
  });

  cutSignals.forEach(({ key, terms }) => {
    if (terms.some((t) => lower.includes(t))) {
      protectedSet.delete(key);
    }
  });

  return Array.from(protectedSet);
};

export default function AICoach({ embedded = false, onClose, onPreferencesChange, onReady }) {
  const [session, setSession] = useState(null);
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [userProfile, setUserProfile] = useState({
    name: '',
    age: '',
    profession: ''
  });
  const [preferences, setPreferences] = useState({ protectedCategories: [] });
  const [showProfileForm, setShowProfileForm] = useState(true);
  const messagesEndRef = useRef(null);

  // Auto-scroll to bottom of messages
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    if (onPreferencesChange) {
      onPreferencesChange(preferences);
    }
  }, [preferences, onPreferencesChange]);

  // Start a new coaching session
  const startSession = async () => {
    if (!userProfile.name.trim()) {
      alert('Please enter your name to start');
      return;
    }

    setIsLoading(true);
    try {
      const response = await fetch(`${API_BASE}/ai/session/start`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(userProfile)
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const sessionData = await response.json();
      setSession(sessionData);
      setShowProfileForm(false);

      const derived = derivePreferencesFromProfile(userProfile);
      if (derived.length) {
        setPreferences((prev) => ({
          ...prev,
          protectedCategories: Array.from(new Set([...(prev.protectedCategories || []), ...derived]))
        }));
      }
      
      // Add welcome messages
      setMessages([
        { 
          type: 'ai', 
          content: sessionData.welcome_message,
          timestamp: new Date().toLocaleTimeString()
        },
        { 
          type: 'ai', 
          content: sessionData.first_question,
          timestamp: new Date().toLocaleTimeString()
        }
      ]);
    } catch (error) {
      console.error('Failed to start session:', error);
      alert('Failed to start AI coaching session. Please make sure the backend is running on port 5001.');
    } finally {
      setIsLoading(false);
    }
  };

  // Send message to AI coach
  const sendMessage = async () => {
    if (!inputMessage.trim() || !session) return;

    const userMessage = {
      type: 'user',
      content: inputMessage,
      timestamp: new Date().toLocaleTimeString()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');

    // Update preferences heuristically from user text before AI responds
    setPreferences((prev) => {
      const updatedProtected = derivePreferencesFromText(inputMessage, prev.protectedCategories);
      return { ...prev, protectedCategories: updatedProtected };
    });

    setIsLoading(true);

    try {
      const response = await fetch(`${API_BASE}/ai/chat/send`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          session_id: session.session_id,
          message: inputMessage
        })
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const aiResponse = await response.json();
      
      const aiMessage = {
        type: 'ai',
        content: aiResponse.ai_response,
        progress: aiResponse.conversation_progress,
        insights: aiResponse.diagnostic_insights,
        timestamp: new Date().toLocaleTimeString()
      };

      setMessages(prev => [...prev, aiMessage]);

      if (onReady) {
        onReady({
          preferences,
          progress: aiResponse.conversation_progress,
          sessionId: session.session_id
        });
      }

      // Check if conversation is complete
      if (aiResponse.conversation_progress >= 0.8) {
        setTimeout(() => {
          generateInsights();
        }, 1000);
      }
    } catch (error) {
      console.error('Failed to send message:', error);
      const errorMessage = {
        type: 'ai',
        content: "I'm having trouble responding right now. Please try again.",
        timestamp: new Date().toLocaleTimeString()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  // Generate final insights
  const generateInsights = async () => {
    if (!session) return;

    setIsLoading(true);
    try {
      const response = await fetch(`${API_BASE}/ai/session/${session.session_id}/insights`);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const insights = await response.json();
      
      const insightsMessage = {
        type: 'insights',
        content: "Based on our conversation, here are my insights:",
        insights: insights,
        timestamp: new Date().toLocaleTimeString()
      };

      setMessages(prev => [...prev, insightsMessage]);
    } catch (error) {
      console.error('Failed to generate insights:', error);
    } finally {
      setIsLoading(false);
    }
  };

  // Generate video summary (lightweight backend helper)
  const generateVideoSummary = async () => {
    if (!session) return;

    try {
      const response = await fetch(`${API_BASE}/ai/generate-video/${session.session_id}`, {
        method: 'POST'
      });
      const result = await response.json();

      if (result.success) {
        const videoMessage = {
          type: 'video',
          content: '🎬 Your personalized financial guide is ready!',
          videoPath: result.video_path,
          pattern: result.pattern,
          timestamp: new Date().toLocaleTimeString()
        };
        setMessages(prev => [...prev, videoMessage]);
      } else {
        alert('Video generation failed: ' + (result.error || 'Unknown error'));
      }
    } catch (error) {
      console.error('Video generation error:', error);
      alert('Video service unavailable - check backend');
    }
  };

  // Handle Enter key press
  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  // Reset session
  const resetSession = () => {
    setSession(null);
    setMessages([]);
    setShowProfileForm(true);
    setUserProfile({ name: '', age: '', profession: '' });
    setPreferences({ protectedCategories: [] });
    if (onReady) {
      onReady(null);
    }
  };

  const toggleProtectedCategory = (category) => {
    setPreferences((prev) => {
      const existing = new Set(prev.protectedCategories || []);
      if (existing.has(category)) {
        existing.delete(category);
      } else {
        existing.add(category);
      }
      return { ...prev, protectedCategories: Array.from(existing) };
    });
  };

  const PreferenceSelector = () => (
    <div style={{ marginTop: '12px' }}>
      <p style={{ color: '#666', marginBottom: '8px', fontSize: '13px' }}>Tell the coach what spending to protect:</p>
      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
        {['dining', 'entertainment', 'shopping', 'transportation', 'other'].map((cat) => {
          const active = preferences.protectedCategories?.includes(cat);
          return (
            <button
              key={cat}
              type="button"
              onClick={() => toggleProtectedCategory(cat)}
              style={{
                padding: '8px 12px',
                borderRadius: '999px',
                border: active ? '2px solid #003E5C' : '1px solid #e1e5e9',
                backgroundColor: active ? '#e7f3ff' : '#f8f9fa',
                color: '#003E5C',
                fontWeight: 600,
                cursor: 'pointer',
                textTransform: 'capitalize',
                fontSize: '12px'
              }}
            >
              {active ? 'Protect ' : 'Okay to cut '} {cat}
            </button>
          );
        })}
      </div>
    </div>
  );

  const headerBlock = embedded ? (
    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: '12px', marginBottom: '12px' }}>
      <div>
        <h2 style={{ fontWeight: 800, margin: 0, color: '#003E5C' }}>AI Coach</h2>
        <p style={{color: '#33566f', fontSize: '14px', margin: '4px 0 0 0'}}>Personalized guidance without leaving CapCoach</p>
      </div>
      {onClose && (
        <button
          onClick={onClose}
          aria-label="Close AI Coach"
          style={{
            background: 'transparent',
            border: '1px solid #e1e5e9',
            borderRadius: '50%',
            width: '36px',
            height: '36px',
            fontSize: '18px',
            cursor: 'pointer',
            color: '#003E5C'
          }}
        >
          ×
        </button>
      )}
    </div>
  ) : (
    <>
      <br/>
      <h1 style={{fontWeight: 800}}>AI Financial Coach</h1>
      <p style={{color: '#666', fontSize: '18px'}}>Get personalized financial advice based on your emotions and behaviors</p>
      <br/>
    </>
  );

  return (
    <div
      className="dashboard-style"
      style={embedded ? { padding: '12px', height: '100%', maxHeight: '100%', display: 'flex', flexDirection: 'column', overflowY: 'auto', backgroundColor: '#f4f6f9' } : { backgroundColor: '#f4f6f9' }}
    >
      {headerBlock}

      {showProfileForm ? (
        <Card style={{ padding: '30px', textAlign: 'center', backgroundColor: '#f8f9fa', border: 'none', boxShadow: '0 1px 3px rgba(0, 0, 0, 0.15)' }}>
          <h3 style={{color: '#003E5C', marginBottom: '20px'}}>Let's Get Started</h3>
          <p style={{color: '#666', marginBottom: '24px'}}>Tell me a bit about yourself so I can provide personalized guidance:</p>
          
          <div style={{display: 'flex', flexDirection: 'column', gap: '16px', maxWidth: '400px', margin: '0 auto'}}>
            <input
              type="text"
              placeholder="Your Name"
              value={userProfile.name}
              onChange={(e) => setUserProfile({...userProfile, name: e.target.value})}
              style={{
                padding: '12px',
                border: '2px solid #e1e5e9',
                borderRadius: '8px',
                fontSize: '16px',
                transition: 'border-color 0.3s'
              }}
            />
            <input
              type="text"
              placeholder="Age"
              value={userProfile.age}
              onChange={(e) => setUserProfile({...userProfile, age: e.target.value})}
              style={{
                padding: '12px',
                border: '2px solid #e1e5e9',
                borderRadius: '8px',
                fontSize: '16px'
              }}
            />
            <input
              type="text"
              placeholder="Profession"
              value={userProfile.profession}
              onChange={(e) => setUserProfile({...userProfile, profession: e.target.value})}
              style={{
                padding: '12px',
                border: '2px solid #e1e5e9',
                borderRadius: '8px',
                fontSize: '16px'
              }}
            />
            <PreferenceSelector />
            <button 
              onClick={startSession} 
              disabled={isLoading || !userProfile.name.trim()}
              style={{
                padding: '12px 24px',
                backgroundColor: isLoading || !userProfile.name.trim() ? '#ccc' : '#003E5C',
                color: 'white',
                border: 'none',
                borderRadius: '8px',
                fontSize: '16px',
                cursor: isLoading || !userProfile.name.trim() ? 'not-allowed' : 'pointer',
                fontWeight: 600
              }}
            >
              {isLoading ? 'Starting...' : 'Start Coaching Session'}
            </button>
          </div>
        </Card>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', height: embedded ? '100%' : '70vh', backgroundColor: 'white', borderRadius: '12px', boxShadow: '0 1px 8px rgba(0, 62, 92, 0.15)' }}>
          {/* Chat Header */}
          <div style={{ padding: '16px 20px', borderBottom: '1px solid #e1e5e9', background: 'linear-gradient(90deg, #f6fbff 0%, #eef5fb 100%)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div>
              <h3 style={{ color: '#003E5C', margin: 0 }}>Session with {userProfile.name}</h3>
              <span style={{ fontSize: '12px', color: '#666' }}>ID: {session?.session_id}</span>
            </div>
            <div style={{ display: 'flex', gap: '10px', alignItems: 'center' }}>
              <button 
                onClick={generateVideoSummary}
                style={{
                  padding: '8px 14px',
                  backgroundColor: '#28a745',
                  color: 'white',
                  border: 'none',
                  borderRadius: '6px',
                  cursor: 'pointer',
                  fontSize: '14px',
                  fontWeight: 700,
                  boxShadow: '0 2px 6px rgba(0,0,0,0.12)'
                }}
              >
                🎬 Video
              </button>
              <button 
                onClick={resetSession}
                style={{
                  padding: '8px 16px',
                  backgroundColor: '#6c757d',
                  color: 'white',
                  border: 'none',
                  borderRadius: '6px',
                  cursor: 'pointer',
                  fontSize: '14px'
                }}
              >
                New Session
              </button>
            </div>
          </div>

          {/* Chat Messages */}
          <div style={{ flex: 1, overflowY: 'auto', padding: '16px 20px', backgroundColor: '#f8fafc', display: 'flex', flexDirection: 'column', gap: '12px' }}>
            <PreferenceSelector />
            {messages.map((message, index) => (
              <div key={index} style={{ 
                padding: '16px', 
                borderRadius: '12px', 
                maxWidth: '80%',
                backgroundColor: message.type === 'user' ? '#003E5C' : 'white',
                color: message.type === 'user' ? 'white' : '#333',
                border: message.type === 'ai' || message.type === 'video' ? '1px solid #e1e5e9' : 'none',
                marginLeft: message.type === 'user' ? 'auto' : '0',
                borderBottomRightRadius: message.type === 'user' ? '4px' : '12px',
                borderBottomLeftRadius: message.type === 'ai' || message.type === 'video' ? '4px' : '12px',
                borderTopLeftRadius: message.type === 'ai' || message.type === 'video' ? '4px' : '12px',
                borderTopRightRadius: message.type === 'user' ? '4px' : '12px',
                boxShadow: message.type === 'user' ? '0 4px 10px rgba(0, 62, 92, 0.25)' : '0 2px 6px rgba(0,0,0,0.08)'
              }}>
                <div style={{ marginBottom: '8px', lineHeight: '1.5' }}>
                  {message.content}
                </div>
                
                {message.insights && message.type === 'insights' && (
                  <Card style={{ marginTop: '12px', backgroundColor: '#e7f3ff', border: '1px solid #b3d9ff' }}>
                    <Card.Body>
                      <h5 style={{ color: '#003E5C', marginBottom: '12px' }}>Financial Behavior Insights:</h5>
                      <div style={{ marginBottom: '8px' }}>
                        <strong>Pattern:</strong> {message.insights.financial_behavior?.pattern}
                      </div>
                      <div style={{ marginBottom: '12px' }}>
                        <strong>Advice:</strong> {message.insights.personalized_advice}
                      </div>
                      <div>
                        <strong>Suggested Strategies:</strong>
                        <ul style={{ margin: '8px 0 0 0', paddingLeft: '20px' }}>
                          {message.insights.financial_behavior?.suggested_strategies?.map((strategy, i) => (
                            <li key={i} style={{ marginBottom: '4px' }}>{strategy}</li>
                          ))}
                        </ul>
                      </div>
                    </Card.Body>
                  </Card>
                )}

                {message.type === 'video' && (
                  <Card style={{ marginTop: '12px', backgroundColor: '#e8f5e8', border: '1px solid #4CAF50', boxShadow: '0 2px 6px rgba(0,0,0,0.08)' }}>
                    <Card.Body>
                      <h5 style={{ color: '#2e7d32', marginBottom: '12px' }}>🎬 Personalized Video Guide</h5>
                      <div style={{ marginBottom: '8px' }}>
                        <strong>Pattern:</strong> {message.pattern}
                      </div>
                      <div style={{ marginBottom: '12px', wordBreak: 'break-all' }}>
                        <strong>File:</strong> {message.videoPath}
                      </div>
                      <button 
                        onClick={() => {
                          if (message.videoPath.endsWith('.txt')) {
                            alert(`Open the file: ${message.videoPath}\n\nContains your personalized financial guidance!`);
                          } else {
                            alert(`Video ready: ${message.videoPath}`);
                          }
                        }}
                        style={{
                          padding: '8px 16px',
                          backgroundColor: '#4CAF50',
                          color: 'white',
                          border: 'none',
                          borderRadius: '6px',
                          cursor: 'pointer',
                          fontWeight: 700
                        }}
                      >
                        View Video Guide
                      </button>
                    </Card.Body>
                  </Card>
                )}

                {message.progress && (
                  <div style={{ marginTop: '12px', fontSize: '14px', color: '#666' }}>
                    <div style={{ 
                      background: '#e1e5e9', 
                      borderRadius: '10px', 
                      height: '6px', 
                      marginBottom: '4px',
                      overflow: 'hidden'
                    }}>
                      <div 
                        style={{ 
                          background: '#28a745', 
                          height: '100%', 
                          borderRadius: '10px',
                          width: `${message.progress * 100}%`,
                          transition: 'width 0.3s ease'
                        }} 
                      ></div>
                    </div>
                    <span>Progress: {Math.round(message.progress * 100)}%</span>
                  </div>
                )}
                
                <div style={{ 
                  fontSize: '12px', 
                  opacity: 0.7, 
                  textAlign: 'right', 
                  marginTop: '8px' 
                }}>
                  {message.timestamp}
                </div>
              </div>
            ))}
            
            {isLoading && (
              <div style={{ 
                marginBottom: '16px', 
                padding: '16px', 
                borderRadius: '12px', 
                maxWidth: '80%',
                backgroundColor: 'white',
                border: '1px solid #e1e5e9',
                borderBottomLeftRadius: '4px'
              }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <span>Thinking</span>
                  <div style={{ display: 'flex', gap: '4px' }}>
                    <span style={{
                      height: '8px',
                      width: '8px',
                      borderRadius: '50%',
                      backgroundColor: '#003E5C',
                      animation: 'typing 1.4s infinite ease-in-out'
                    }}></span>
                    <span style={{
                      height: '8px',
                      width: '8px',
                      borderRadius: '50%',
                      backgroundColor: '#003E5C',
                      animation: 'typing 1.4s infinite ease-in-out',
                      animationDelay: '0.16s'
                    }}></span>
                    <span style={{
                      height: '8px',
                      width: '8px',
                      borderRadius: '50%',
                      backgroundColor: '#003E5C',
                      animation: 'typing 1.4s infinite ease-in-out',
                      animationDelay: '0.32s'
                    }}></span>
                  </div>
                </div>
              </div>
            )}
            
            <div ref={messagesEndRef} />
          </div>

          {/* Chat Input */}
          <div style={{ padding: '14px 16px', borderTop: '1px solid #e1e5e9', backgroundColor: 'white' }}>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr auto', gap: '10px', alignItems: 'center', marginBottom: '12px' }}>
              <input
                type="text"
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Type your message here..."
                disabled={isLoading}
                style={{
                  flex: 1,
                  padding: '12px 14px',
                  border: '2px solid #e1e5e9',
                  borderRadius: '10px',
                  fontSize: '15px',
                  outline: 'none',
                  minWidth: 0
                }}
              />
              <button 
                onClick={sendMessage} 
                disabled={isLoading || !inputMessage.trim()}
                style={{
                  padding: '12px 18px',
                  backgroundColor: isLoading || !inputMessage.trim() ? '#ccc' : '#003E5C',
                  color: 'white',
                  border: 'none',
                  borderRadius: '10px',
                  cursor: isLoading || !inputMessage.trim() ? 'not-allowed' : 'pointer',
                  fontSize: '15px',
                  fontWeight: 700,
                  whiteSpace: 'nowrap'
                }}
              >
                Send
              </button>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', flexWrap: 'wrap', fontSize: '14px', color: '#666' }}>
              <span>Try asking:</span>
              <button 
                onClick={() => setInputMessage("I feel anxious about money")}
                style={{
                  padding: '6px 12px',
                  backgroundColor: '#f8f9fa',
                  border: '1px solid #e1e5e9',
                  borderRadius: '4px',
                  cursor: 'pointer',
                  fontSize: '14px'
                }}
              >
                "I feel anxious about money"
              </button>
              <button 
                onClick={() => setInputMessage("How can I save more?")}
                style={{
                  padding: '6px 12px',
                  backgroundColor: '#f8f9fa',
                  border: '1px solid #e1e5e9',
                  borderRadius: '4px',
                  cursor: 'pointer',
                  fontSize: '14px'
                }}
              >
                "How can I save more?"
              </button>
            </div>
          </div>
        </div>
      )}

      <style jsx>{`
        @keyframes typing {
          0%, 80%, 100% { transform: scale(0.8); opacity: 0.5; }
          40% { transform: scale(1); opacity: 1; }
        }
      `}</style>
    </div>
  );
}
