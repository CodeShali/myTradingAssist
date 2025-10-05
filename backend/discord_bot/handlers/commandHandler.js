/**
 * Command handler for Discord bot commands
 */
import { EmbedBuilder } from 'discord.js';
import axios from 'axios';
import { logger } from '../utils/logger.js';

export class CommandHandler {
    constructor(client, redisClient) {
        this.client = client;
        this.redisClient = redisClient;
        this.apiUrl = process.env.API_GATEWAY_URL || 'http://localhost:3000';
        this.prefix = '!';
    }

    async handleMessage(message) {
        if (!message.content.startsWith(this.prefix)) return;

        const args = message.content.slice(this.prefix.length).trim().split(/ +/);
        const command = args.shift().toLowerCase();

        try {
            switch (command) {
                case 'signals':
                    await this.showPendingSignals(message);
                    break;
                case 'positions':
                    await this.showPositions(message);
                    break;
                case 'pnl':
                    await this.showPnL(message);
                    break;
                case 'config':
                    await this.showConfig(message);
                    break;
                case 'pause':
                    await this.pauseTrading(message);
                    break;
                case 'resume':
                    await this.resumeTrading(message);
                    break;
                case 'help':
                    await this.showHelp(message);
                    break;
                default:
                    await message.reply('Unknown command. Use `!help` for available commands.');
            }
        } catch (error) {
            logger.error(`Error handling command ${command}:`, error);
            await message.reply('An error occurred processing your command.');
        }
    }

    async showPendingSignals(message) {
        try {
            const userId = await this.getUserId(message.author.id);
            if (!userId) {
                await message.reply('Your Discord account is not linked. Please link it in the web dashboard.');
                return;
            }

            const response = await axios.get(`${this.apiUrl}/api/signals/pending?user_id=${userId}`);
            const signals = response.data;

            if (!signals || signals.length === 0) {
                await message.reply('No pending signals.');
                return;
            }

            const embed = new EmbedBuilder()
                .setColor(0x0099FF)
                .setTitle('📋 Pending Trade Signals')
                .setDescription(`You have ${signals.length} pending signal(s)`)
                .setTimestamp();

            signals.forEach((signal, index) => {
                const timeRemaining = Math.floor((new Date(signal.expires_at) - new Date()) / 1000);
                embed.addFields({
                    name: `${index + 1}. ${signal.symbol} - ${signal.strategy_type}`,
                    value: `Strike: $${signal.strike_price} | Expires in: ${timeRemaining}s`,
                    inline: false
                });
            });

            await message.reply({ embeds: [embed] });

        } catch (error) {
            logger.error('Error showing pending signals:', error);
            await message.reply('Failed to fetch pending signals.');
        }
    }

    async showPositions(message) {
        try {
            const userId = await this.getUserId(message.author.id);
            if (!userId) {
                await message.reply('Your Discord account is not linked.');
                return;
            }

            const response = await axios.get(`${this.apiUrl}/api/positions?user_id=${userId}`);
            const portfolio = response.data;

            if (!portfolio.positions || portfolio.positions.length === 0) {
                await message.reply('No open positions.');
                return;
            }

            const embed = new EmbedBuilder()
                .setColor(0x00FF00)
                .setTitle('📊 Open Positions')
                .setDescription(`Total Unrealized P&L: $${portfolio.total_unrealized_pnl.toFixed(2)}`)
                .setTimestamp();

            portfolio.positions.forEach((pos, index) => {
                const pnlEmoji = pos.unrealized_pnl >= 0 ? '📈' : '📉';
                embed.addFields({
                    name: `${index + 1}. ${pos.symbol} - ${pos.strategy_type}`,
                    value: `${pnlEmoji} P&L: $${pos.unrealized_pnl.toFixed(2)} (${pos.unrealized_pnl_pct.toFixed(2)}%)`,
                    inline: false
                });
            });

            await message.reply({ embeds: [embed] });

        } catch (error) {
            logger.error('Error showing positions:', error);
            await message.reply('Failed to fetch positions.');
        }
    }

    async showPnL(message) {
        try {
            const userId = await this.getUserId(message.author.id);
            if (!userId) {
                await message.reply('Your Discord account is not linked.');
                return;
            }

            const response = await axios.get(`${this.apiUrl}/api/analytics/pnl?user_id=${userId}`);
            const pnl = response.data;

            const totalPnL = (pnl.daily_realized_pnl || 0) + (pnl.total_unrealized_pnl || 0);
            const color = totalPnL >= 0 ? 0x00FF00 : 0xFF0000;

            const embed = new EmbedBuilder()
                .setColor(color)
                .setTitle('💰 Profit & Loss Summary')
                .addFields(
                    { name: 'Today\'s Realized P&L', value: `$${(pnl.daily_realized_pnl || 0).toFixed(2)}`, inline: true },
                    { name: 'Unrealized P&L', value: `$${(pnl.total_unrealized_pnl || 0).toFixed(2)}`, inline: true },
                    { name: 'Total P&L', value: `$${totalPnL.toFixed(2)}`, inline: true },
                    { name: 'Open Positions', value: (pnl.open_positions || 0).toString(), inline: true },
                    { name: 'Trades Today', value: (pnl.trades_today || 0).toString(), inline: true }
                )
                .setTimestamp();

            await message.reply({ embeds: [embed] });

        } catch (error) {
            logger.error('Error showing P&L:', error);
            await message.reply('Failed to fetch P&L data.');
        }
    }

    async showConfig(message) {
        try {
            const userId = await this.getUserId(message.author.id);
            if (!userId) {
                await message.reply('Your Discord account is not linked.');
                return;
            }

            const response = await axios.get(`${this.apiUrl}/api/users/${userId}/config`);
            const config = response.data;

            const embed = new EmbedBuilder()
                .setColor(0x0099FF)
                .setTitle('⚙️ Trading Configuration')
                .addFields(
                    { name: 'Max Position Size', value: `${config.max_position_size_pct}%`, inline: true },
                    { name: 'Max Daily Trades', value: config.max_daily_trades.toString(), inline: true },
                    { name: 'Profit Target', value: `${config.default_profit_target_pct}%`, inline: true },
                    { name: 'Stop Loss', value: `${config.default_stop_loss_pct}%`, inline: true },
                    { name: 'Auto-Sell', value: config.auto_sell_enabled ? '✅ Enabled' : '❌ Disabled', inline: true },
                    { name: 'News Sentiment', value: config.news_sentiment_enabled ? '✅ Enabled' : '❌ Disabled', inline: true }
                )
                .setFooter({ text: 'Update configuration in the web dashboard' })
                .setTimestamp();

            await message.reply({ embeds: [embed] });

        } catch (error) {
            logger.error('Error showing config:', error);
            await message.reply('Failed to fetch configuration.');
        }
    }

    async pauseTrading(message) {
        try {
            const userId = await this.getUserId(message.author.id);
            if (!userId) {
                await message.reply('Your Discord account is not linked.');
                return;
            }

            await axios.post(`${this.apiUrl}/api/trading/pause`, { user_id: userId });
            await message.reply('⏸️ Trading paused. You will not receive new signals until you resume.');

        } catch (error) {
            logger.error('Error pausing trading:', error);
            await message.reply('Failed to pause trading.');
        }
    }

    async resumeTrading(message) {
        try {
            const userId = await this.getUserId(message.author.id);
            if (!userId) {
                await message.reply('Your Discord account is not linked.');
                return;
            }

            await axios.post(`${this.apiUrl}/api/trading/resume`, { user_id: userId });
            await message.reply('▶️ Trading resumed. You will now receive new signals.');

        } catch (error) {
            logger.error('Error resuming trading:', error);
            await message.reply('Failed to resume trading.');
        }
    }

    async showHelp(message) {
        const embed = new EmbedBuilder()
            .setColor(0x0099FF)
            .setTitle('📚 Trading Bot Commands')
            .setDescription('Available commands for the AI-Assisted Options Trading Bot')
            .addFields(
                { name: '!signals', value: 'Show pending trade signals', inline: false },
                { name: '!positions', value: 'Show open positions', inline: false },
                { name: '!pnl', value: 'Show profit & loss summary', inline: false },
                { name: '!config', value: 'Show trading configuration', inline: false },
                { name: '!pause', value: 'Pause signal generation', inline: false },
                { name: '!resume', value: 'Resume signal generation', inline: false },
                { name: '!help', value: 'Show this help message', inline: false }
            )
            .setFooter({ text: 'For more features, visit the web dashboard' })
            .setTimestamp();

        await message.reply({ embeds: [embed] });
    }

    async handleSlashCommand(interaction) {
        // Placeholder for slash commands implementation
        await interaction.reply({ content: 'Slash commands coming soon!', ephemeral: true });
    }

    async getUserId(discordUserId) {
        try {
            const response = await axios.get(`${this.apiUrl}/api/users/by-discord/${discordUserId}`);
            return response.data.user_id;
        } catch (error) {
            logger.error('Error fetching user ID:', error);
            return null;
        }
    }
}
