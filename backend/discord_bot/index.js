/**
 * Discord Bot for AI-Assisted Options Trading Platform
 */
import { Client, GatewayIntentBits, EmbedBuilder, ActionRowBuilder, ButtonBuilder, ButtonStyle } from 'discord.js';
import { createClient } from 'redis';
import dotenv from 'dotenv';
import { logger } from './utils/logger.js';
import { SignalHandler } from './handlers/signalHandler.js';
import { CommandHandler } from './handlers/commandHandler.js';

dotenv.config();

class TradingBot {
    constructor() {
        this.client = new Client({
            intents: [
                GatewayIntentBits.Guilds,
                GatewayIntentBits.GuildMessages,
                GatewayIntentBits.MessageContent,
                GatewayIntentBits.GuildMessageReactions
            ]
        });

        this.redisClient = createClient({
            url: process.env.REDIS_URL || 'redis://localhost:6379'
        });

        this.signalHandler = new SignalHandler(this.client, this.redisClient);
        this.commandHandler = new CommandHandler(this.client, this.redisClient);

        this.setupEventHandlers();
    }

    setupEventHandlers() {
        // Bot ready event
        this.client.once('ready', async () => {
            logger.info(`Discord bot logged in as ${this.client.user.tag}`);
            this.client.user.setActivity('Options Trading', { type: 'WATCHING' });
            
            // Send startup notification
            await this.sendStartupNotification();
        });

        // Message commands
        this.client.on('messageCreate', async (message) => {
            if (message.author.bot) return;
            await this.commandHandler.handleMessage(message);
        });

        // Reaction events for signal confirmation
        this.client.on('messageReactionAdd', async (reaction, user) => {
            if (user.bot) return;
            await this.signalHandler.handleReaction(reaction, user, 'add');
        });

        this.client.on('messageReactionRemove', async (reaction, user) => {
            if (user.bot) return;
            await this.signalHandler.handleReaction(reaction, user, 'remove');
        });

        // Interaction events (slash commands, buttons)
        this.client.on('interactionCreate', async (interaction) => {
            if (interaction.isCommand()) {
                await this.commandHandler.handleSlashCommand(interaction);
            } else if (interaction.isButton()) {
                await this.signalHandler.handleButtonInteraction(interaction);
            }
        });

        // Error handling
        this.client.on('error', (error) => {
            logger.error('Discord client error:', error);
        });

        process.on('unhandledRejection', (error) => {
            logger.error('Unhandled promise rejection:', error);
        });
    }

    async start() {
        try {
            // Connect to Redis
            await this.redisClient.connect();
            logger.info('Connected to Redis');

            // Subscribe to Redis channels
            await this.subscribeToSignals();

            // Login to Discord
            await this.client.login(process.env.DISCORD_BOT_TOKEN);
        } catch (error) {
            if (error.message && error.message.includes('disallowed intents')) {
                logger.error('❌ Discord Bot Error: MESSAGE CONTENT INTENT not enabled!');
                logger.error('');
                logger.error('📝 To fix this:');
                logger.error('1. Go to: https://discord.com/developers/applications');
                logger.error('2. Select your application');
                logger.error('3. Go to "Bot" section');
                logger.error('4. Scroll to "Privileged Gateway Intents"');
                logger.error('5. Enable "MESSAGE CONTENT INTENT"');
                logger.error('6. Click "Save Changes"');
                logger.error('7. Restart this bot: docker compose restart discord_bot');
                logger.error('');
                logger.error('⚠️  Platform will continue to work without Discord notifications');
            } else {
                logger.error('Failed to start bot:', error);
            }
            // Don't exit - let Docker restart and retry
            await new Promise(resolve => setTimeout(resolve, 30000)); // Wait 30s before retry
            process.exit(1);
        }
    }

    async sendStartupNotification() {
        try {
            const channel = await this.client.channels.fetch(process.env.DISCORD_UPDATES_CHANNEL_ID || process.env.DISCORD_CHANNEL_ID);
            if (!channel) return;

            // Test backend APIs
            const apiTests = await this.testBackendAPIs();
            
            const embed = {
                color: 0x00ff00, // Green
                title: '🚀 OptionsAI Platform Started',
                description: 'AI-Assisted Options Trading Platform is now online!',
                fields: [
                    {
                        name: '📊 System Status',
                        value: `✅ Discord Bot: Connected\n✅ Redis: Connected\n✅ Trading Mode: ${process.env.TRADING_MODE || 'paper'}`,
                        inline: false
                    },
                    {
                        name: '🔧 Backend API Tests',
                        value: apiTests,
                        inline: false
                    },
                    {
                        name: '⚙️ Configuration',
                        value: `Server: ${process.env.DISCORD_GUILD_ID}\nChannels: ${this.getChannelCount()} configured`,
                        inline: false
                    }
                ],
                timestamp: new Date().toISOString(),
                footer: {
                    text: 'OptionsAI Trading Platform'
                }
            };

            await channel.send({ embeds: [embed] });
            logger.info('Startup notification sent to Discord');
        } catch (error) {
            logger.error('Failed to send startup notification:', error);
        }
    }

    async testBackendAPIs() {
        const results = [];
        
        try {
            // Test API Gateway
            const apiResponse = await fetch('http://api_gateway:3000/health');
            results.push(apiResponse.ok ? '✅ API Gateway: Healthy' : '❌ API Gateway: Down');
        } catch (error) {
            results.push('❌ API Gateway: Unreachable');
        }

        try {
            // Test Database via Redis (we know Redis works if we're here)
            results.push('✅ Redis: Connected');
        } catch (error) {
            results.push('❌ Redis: Error');
        }

        return results.join('\n');
    }

    getChannelCount() {
        let count = 0;
        if (process.env.DISCORD_CHANNEL_ID) count++;
        if (process.env.DISCORD_SIGNALS_CHANNEL_ID) count++;
        if (process.env.DISCORD_TRADES_CHANNEL_ID) count++;
        if (process.env.DISCORD_ALERTS_CHANNEL_ID) count++;
        if (process.env.DISCORD_UPDATES_CHANNEL_ID) count++;
        return count;
    }

    async subscribeToSignals() {
        // Create a duplicate client for pub/sub
        const subscriber = this.redisClient.duplicate();
        await subscriber.connect();

        // Subscribe to all signals channel
        await subscriber.subscribe('signals:all', async (message) => {
            try {
                const signal = JSON.parse(message);
                await this.signalHandler.handleNewSignal(signal);
            } catch (error) {
                logger.error('Error handling signal:', error);
            }
        });

        // Subscribe to position updates
        await subscriber.subscribe('positions:*', async (message) => {
            try {
                const update = JSON.parse(message);
                await this.signalHandler.handlePositionUpdate(update);
            } catch (error) {
                logger.error('Error handling position update:', error);
            }
        });

        logger.info('Subscribed to Redis channels');
    }

    async stop() {
        logger.info('Shutting down bot...');
        await this.redisClient.quit();
        await this.client.destroy();
        logger.info('Bot shut down complete');
    }
}

// Start the bot
const bot = new TradingBot();

// Graceful shutdown
process.on('SIGINT', async () => {
    await bot.stop();
    process.exit(0);
});

process.on('SIGTERM', async () => {
    await bot.stop();
    process.exit(0);
});

bot.start();
