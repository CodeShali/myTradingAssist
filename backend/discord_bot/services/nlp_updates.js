/**
 * NLP-Based Discord Updates Service
 * Sends natural language process updates to Discord channels
 */

const { OpenAI } = require('openai');
const logger = require('../utils/logger');

class NLPUpdatesService {
  constructor(client) {
    this.discordClient = client;
    this.openaiEnabled = !!process.env.OPENAI_API_KEY;
    
    if (this.openaiEnabled) {
      this.openai = new OpenAI({
        apiKey: process.env.OPENAI_API_KEY,
      });
      this.model = process.env.OPENAI_MODEL || 'gpt-4';
      logger.info('OpenAI NLP updates enabled');
    } else {
      logger.info('OpenAI NLP updates disabled (no API key)');
    }
    
    // Channel IDs
    this.channels = {
      main: process.env.DISCORD_CHANNEL_ID,
      signals: process.env.DISCORD_SIGNALS_CHANNEL_ID,
      trades: process.env.DISCORD_TRADES_CHANNEL_ID,
      alerts: process.env.DISCORD_ALERTS_CHANNEL_ID,
      updates: process.env.DISCORD_UPDATES_CHANNEL_ID,
    };
  }

  /**
   * Send pre-market analysis update
   */
  async sendPreMarketUpdate(marketData, watchlistSymbols) {
    const channelId = this.channels.updates || this.channels.main;
    if (!channelId) return;

    try {
      let message;
      
      if (this.openaiEnabled) {
        // Enhanced NLP message
        message = await this.generatePreMarketNLP(marketData, watchlistSymbols);
      } else {
        // Standard message
        message = this.formatPreMarketStandard(marketData, watchlistSymbols);
      }
      
      await this.sendToChannel(channelId, message);
      logger.info('Pre-market update sent');
    } catch (error) {
      logger.error('Error sending pre-market update:', error);
    }
  }

  /**
   * Send process status update
   */
  async sendProcessUpdate(processName, status, details = {}) {
    const channelId = this.channels.updates || this.channels.main;
    if (!channelId) return;

    try {
      const emojis = {
        started: '🚀',
        running: '⚙️',
        completed: '✅',
        error: '❌',
        warning: '⚠️',
      };

      const emoji = emojis[status] || '📊';
      
      let message;
      
      if (this.openaiEnabled && details.description) {
        // Enhanced NLP message
        message = await this.generateProcessUpdateNLP(processName, status, details);
      } else {
        // Standard message
        message = `${emoji} **${processName}** - ${status}\n`;
        if (details.message) {
          message += `\n${details.message}`;
        }
      }
      
      await this.sendToChannel(channelId, message);
    } catch (error) {
      logger.error('Error sending process update:', error);
    }
  }

  /**
   * Send signal generation update
   */
  async sendSignalGenerationUpdate(symbolsScanned, signalsFound, topSignals) {
    const channelId = this.channels.updates || this.channels.main;
    if (!channelId) return;

    try {
      let message;
      
      if (this.openaiEnabled) {
        message = await this.generateSignalUpdateNLP(symbolsScanned, signalsFound, topSignals);
      } else {
        message = `🤖 **Signal Generation Complete**\n\n`;
        message += `📊 Scanned: ${symbolsScanned} symbols\n`;
        message += `🎯 Signals Found: ${signalsFound}\n`;
        if (topSignals.length > 0) {
          message += `\n**Top Signals:**\n`;
          topSignals.forEach(s => {
            message += `• ${s.symbol} - ${s.confidence}% confidence\n`;
          });
        }
      }
      
      await this.sendToChannel(channelId, message);
    } catch (error) {
      logger.error('Error sending signal update:', error);
    }
  }

  /**
   * Send position update
   */
  async sendPositionUpdate(position, updateType) {
    const channelId = this.channels.trades || this.channels.main;
    if (!channelId) return;

    try {
      let message;
      
      if (this.openaiEnabled) {
        message = await this.generatePositionUpdateNLP(position, updateType);
      } else {
        message = this.formatPositionStandard(position, updateType);
      }
      
      await this.sendToChannel(channelId, message);
    } catch (error) {
      logger.error('Error sending position update:', error);
    }
  }

  /**
   * Send end-of-day summary
   */
  async sendDailySummary(performanceData) {
    const channelId = this.channels.updates || this.channels.main;
    if (!channelId) return;

    try {
      let message;
      
      if (this.openaiEnabled) {
        message = await this.generateDailySummaryNLP(performanceData);
      } else {
        message = this.formatDailySummaryStandard(performanceData);
      }
      
      await this.sendToChannel(channelId, message);
    } catch (error) {
      logger.error('Error sending daily summary:', error);
    }
  }

  // ========== OpenAI NLP Generators ==========

  async generatePreMarketNLP(marketData, watchlistSymbols) {
    const prompt = `
    Create a friendly pre-market update for options traders:
    
    Market Data:
    - S&P 500: ${marketData.sp500Change || 'N/A'}
    - VIX: ${marketData.vix || 'N/A'}
    - Pre-market volume: ${marketData.volume || 'moderate'}
    
    Watchlist: ${watchlistSymbols.join(', ')}
    
    Include:
    1. Good morning greeting
    2. Brief market overview
    3. Key opportunities or risks
    4. What to watch today
    
    Use emojis and keep it under 200 words.
    `;

    const response = await this.openai.chat.completions.create({
      model: this.model,
      messages: [
        { role: 'system', content: 'You are a friendly trading assistant providing morning updates.' },
        { role: 'user', content: prompt }
      ],
      max_tokens: 300,
      temperature: 0.8,
    });

    return response.choices[0].message.content;
  }

  async generateProcessUpdateNLP(processName, status, details) {
    const prompt = `
    Create a brief update about this trading process:
    
    Process: ${processName}
    Status: ${status}
    Details: ${JSON.stringify(details, null, 2)}
    
    Write 1-2 sentences explaining what's happening in plain English.
    Use appropriate emoji.
    `;

    const response = await this.openai.chat.completions.create({
      model: this.model,
      messages: [
        { role: 'system', content: 'You are a technical assistant explaining trading processes.' },
        { role: 'user', content: prompt }
      ],
      max_tokens: 100,
      temperature: 0.7,
    });

    return response.choices[0].message.content;
  }

  async generateSignalUpdateNLP(symbolsScanned, signalsFound, topSignals) {
    const signalsText = topSignals.map(s => 
      `${s.symbol} (${s.confidence}% confidence)`
    ).join(', ');

    const prompt = `
    Create an update about signal generation:
    
    - Scanned: ${symbolsScanned} symbols
    - Signals found: ${signalsFound}
    - Top signals: ${signalsText}
    
    Write a brief, exciting update (2-3 sentences) about the signals found.
    Include emojis and be encouraging.
    `;

    const response = await this.openai.chat.completions.create({
      model: this.model,
      messages: [
        { role: 'system', content: 'You are an enthusiastic trading assistant.' },
        { role: 'user', content: prompt }
      ],
      max_tokens: 150,
      temperature: 0.8,
    });

    return response.choices[0].message.content;
  }

  async generatePositionUpdateNLP(position, updateType) {
    const prompt = `
    Create a position update message:
    
    Position: ${position.symbol}
    Type: ${updateType}
    Entry: $${position.entryPrice}
    Current: $${position.currentPrice}
    P&L: ${position.pnlPct > 0 ? '+' : ''}${position.pnlPct}%
    
    Write 2-3 sentences about this position update.
    Be informative and use emojis.
    `;

    const response = await this.openai.chat.completions.create({
      model: this.model,
      messages: [
        { role: 'system', content: 'You are a trading assistant providing position updates.' },
        { role: 'user', content: prompt }
      ],
      max_tokens: 150,
      temperature: 0.7,
    });

    return response.choices[0].message.content;
  }

  async generateDailySummaryNLP(performanceData) {
    const prompt = `
    Create an end-of-day trading summary:
    
    Performance:
    - Trades: ${performanceData.tradesExecuted}
    - Win Rate: ${performanceData.winRate}%
    - P&L: $${performanceData.totalPnl > 0 ? '+' : ''}${performanceData.totalPnl}
    - Best Trade: ${performanceData.bestTrade}
    
    Write:
    1. Performance summary (2-3 sentences)
    2. Key insight
    3. Encouraging message for tomorrow
    
    Use emojis and be motivating!
    `;

    const response = await this.openai.chat.completions.create({
      model: this.model,
      messages: [
        { role: 'system', content: 'You are a supportive trading coach.' },
        { role: 'user', content: prompt }
      ],
      max_tokens: 250,
      temperature: 0.8,
    });

    return response.choices[0].message.content;
  }

  // ========== Standard Formatters (Fallback) ==========

  formatPreMarketStandard(marketData, watchlistSymbols) {
    return `🌅 **Pre-Market Analysis Started**\n\n` +
           `📊 Market Overview:\n` +
           `• S&P 500: ${marketData.sp500Change || 'N/A'}\n` +
           `• VIX: ${marketData.vix || 'N/A'}\n\n` +
           `🔍 Scanning ${watchlistSymbols.length} symbols...\n` +
           `⏰ Market opens soon!`;
  }

  formatPositionStandard(position, updateType) {
    const emoji = updateType === 'opened' ? '📈' : '📉';
    return `${emoji} **Position ${updateType}**: ${position.symbol}\n` +
           `💵 Entry: $${position.entryPrice}\n` +
           `📊 P&L: ${position.pnlPct > 0 ? '+' : ''}${position.pnlPct}%`;
  }

  formatDailySummaryStandard(performanceData) {
    return `📊 **Daily Summary**\n\n` +
           `Trades: ${performanceData.tradesExecuted}\n` +
           `Win Rate: ${performanceData.winRate}%\n` +
           `P&L: $${performanceData.totalPnl > 0 ? '+' : ''}${performanceData.totalPnl}\n\n` +
           `Great day! 🚀`;
  }

  // ========== Helper Methods ==========

  async sendToChannel(channelId, message) {
    try {
      const channel = await this.discordClient.channels.fetch(channelId);
      if (channel) {
        await channel.send(message);
      }
    } catch (error) {
      logger.error(`Error sending to channel ${channelId}:`, error);
    }
  }
}

module.exports = NLPUpdatesService;
