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
        this.client.once('ready', () => {
            logger.info(`Discord bot logged in as ${this.client.user.tag}`);
            this.client.user.setActivity('Options Trading', { type: 'WATCHING' });
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

            // Subscribe to signal events
            await this.subscribeToSignals();

            // Login to Discord
            await this.client.login(process.env.DISCORD_BOT_TOKEN);

        } catch (error) {
            logger.error('Failed to start bot:', error);
            process.exit(1);
        }
    }

    async subscribeToSignals() {
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
