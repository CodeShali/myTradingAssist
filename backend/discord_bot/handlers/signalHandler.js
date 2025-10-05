/**
 * Signal handler for trade signal confirmations
 */
import { EmbedBuilder, ActionRowBuilder, ButtonBuilder, ButtonStyle } from 'discord.js';
import axios from 'axios';
import { logger } from '../utils/logger.js';

export class SignalHandler {
    constructor(client, redisClient) {
        this.client = client;
        this.redisClient = redisClient;
        this.apiUrl = process.env.API_GATEWAY_URL || 'http://localhost:3000';
        this.pendingSignals = new Map(); // signalId -> messageId
    }

    async handleNewSignal(signal) {
        try {
            logger.info(`New signal received: ${signal.id} for ${signal.symbol}`);

            // Get user's Discord ID from database
            const discordUserId = await this.getUserDiscordId(signal.user_id);
            
            if (!discordUserId) {
                logger.warn(`No Discord ID found for user ${signal.user_id}`);
                return;
            }

            // Get user from Discord
            const user = await this.client.users.fetch(discordUserId);
            
            if (!user) {
                logger.warn(`Discord user not found: ${discordUserId}`);
                return;
            }

            // Create embed message
            const embed = this.createSignalEmbed(signal);
            
            // Create action buttons
            const row = new ActionRowBuilder()
                .addComponents(
                    new ButtonBuilder()
                        .setCustomId(`confirm_${signal.id}`)
                        .setLabel('✅ Confirm')
                        .setStyle(ButtonStyle.Success),
                    new ButtonBuilder()
                        .setCustomId(`reject_${signal.id}`)
                        .setLabel('❌ Reject')
                        .setStyle(ButtonStyle.Danger),
                    new ButtonBuilder()
                        .setCustomId(`details_${signal.id}`)
                        .setLabel('📊 Details')
                        .setStyle(ButtonStyle.Primary)
                );

            // Send DM to user
            const message = await user.send({
                embeds: [embed],
                components: [row]
            });

            // Store message reference
            this.pendingSignals.set(signal.id, message.id);

            // Set expiration timer
            this.setExpirationTimer(signal.id, signal.expires_at, message);

            logger.info(`Signal ${signal.id} sent to user ${discordUserId}`);

        } catch (error) {
            logger.error('Error handling new signal:', error);
        }
    }

    createSignalEmbed(signal) {
        const expiresAt = new Date(signal.expires_at);
        const timeRemaining = Math.floor((expiresAt - new Date()) / 1000);

        const embed = new EmbedBuilder()
            .setColor(signal.signal_type === 'buy' ? 0x00FF00 : 0xFF0000)
            .setTitle(`🎯 New Trade Signal: ${signal.symbol}`)
            .setDescription(signal.reasoning || 'AI-generated trade opportunity')
            .addFields(
                { name: 'Strategy', value: signal.strategy_type.replace('_', ' ').toUpperCase(), inline: true },
                { name: 'Action', value: signal.signal_type.toUpperCase(), inline: true },
                { name: 'Confidence', value: `${signal.confidence_score}%`, inline: true },
                { name: 'Option', value: signal.option_symbol, inline: false },
                { name: 'Strike', value: `$${signal.strike_price}`, inline: true },
                { name: 'Expiration', value: signal.expiration_date, inline: true },
                { name: 'Type', value: signal.option_type.toUpperCase(), inline: true },
                { name: 'Quantity', value: signal.quantity.toString(), inline: true },
                { name: 'Limit Price', value: signal.limit_price ? `$${signal.limit_price}` : 'Market', inline: true },
                { name: '⏱️ Time Remaining', value: `${timeRemaining}s`, inline: true }
            )
            .setTimestamp()
            .setFooter({ text: `Signal ID: ${signal.id}` });

        return embed;
    }

    async handleButtonInteraction(interaction) {
        try {
            const [action, signalId] = interaction.customId.split('_');

            if (action === 'confirm') {
                await this.confirmSignal(signalId, interaction);
            } else if (action === 'reject') {
                await this.rejectSignal(signalId, interaction);
            } else if (action === 'details') {
                await this.showSignalDetails(signalId, interaction);
            }

        } catch (error) {
            logger.error('Error handling button interaction:', error);
            await interaction.reply({ content: 'An error occurred processing your request.', ephemeral: true });
        }
    }

    async confirmSignal(signalId, interaction) {
        try {
            await interaction.deferReply({ ephemeral: true });

            // Call API to confirm signal
            const response = await axios.post(`${this.apiUrl}/api/signals/${signalId}/confirm`, {
                source: 'discord',
                user_id: interaction.user.id
            });

            if (response.data.success) {
                // Update original message
                const embed = EmbedBuilder.from(interaction.message.embeds[0])
                    .setColor(0x00FF00)
                    .setTitle(`✅ Trade Confirmed: ${response.data.signal.symbol}`);

                await interaction.message.edit({
                    embeds: [embed],
                    components: [] // Remove buttons
                });

                await interaction.editReply({
                    content: '✅ Trade signal confirmed! Executing order...',
                    ephemeral: true
                });

                // Remove from pending
                this.pendingSignals.delete(signalId);

                logger.info(`Signal ${signalId} confirmed by user ${interaction.user.id}`);
            } else {
                await interaction.editReply({
                    content: '❌ Failed to confirm signal. It may have expired.',
                    ephemeral: true
                });
            }

        } catch (error) {
            logger.error('Error confirming signal:', error);
            await interaction.editReply({
                content: '❌ An error occurred confirming the signal.',
                ephemeral: true
            });
        }
    }

    async rejectSignal(signalId, interaction) {
        try {
            await interaction.deferReply({ ephemeral: true });

            // Call API to reject signal
            const response = await axios.post(`${this.apiUrl}/api/signals/${signalId}/reject`, {
                source: 'discord',
                user_id: interaction.user.id
            });

            if (response.data.success) {
                // Update original message
                const embed = EmbedBuilder.from(interaction.message.embeds[0])
                    .setColor(0xFF0000)
                    .setTitle(`❌ Trade Rejected: ${response.data.signal.symbol}`);

                await interaction.message.edit({
                    embeds: [embed],
                    components: [] // Remove buttons
                });

                await interaction.editReply({
                    content: '❌ Trade signal rejected.',
                    ephemeral: true
                });

                // Remove from pending
                this.pendingSignals.delete(signalId);

                logger.info(`Signal ${signalId} rejected by user ${interaction.user.id}`);
            }

        } catch (error) {
            logger.error('Error rejecting signal:', error);
            await interaction.editReply({
                content: '❌ An error occurred rejecting the signal.',
                ephemeral: true
            });
        }
    }

    async showSignalDetails(signalId, interaction) {
        try {
            await interaction.deferReply({ ephemeral: true });

            // Fetch detailed signal information
            const response = await axios.get(`${this.apiUrl}/api/signals/${signalId}`);
            const signal = response.data;

            const detailEmbed = new EmbedBuilder()
                .setColor(0x0099FF)
                .setTitle(`📊 Signal Details: ${signal.symbol}`)
                .addFields(
                    { name: 'Market Conditions', value: this.formatMarketConditions(signal.market_conditions), inline: false },
                    { name: 'AI Reasoning', value: signal.reasoning || 'N/A', inline: false }
                )
                .setTimestamp();

            await interaction.editReply({
                embeds: [detailEmbed],
                ephemeral: true
            });

        } catch (error) {
            logger.error('Error showing signal details:', error);
            await interaction.editReply({
                content: '❌ Failed to fetch signal details.',
                ephemeral: true
            });
        }
    }

    formatMarketConditions(conditions) {
        if (!conditions) return 'N/A';
        
        const parts = [];
        if (conditions.stock_price) parts.push(`Stock Price: $${conditions.stock_price}`);
        if (conditions.historical_volatility) parts.push(`HV: ${conditions.historical_volatility}%`);
        if (conditions.news_sentiment !== null) parts.push(`Sentiment: ${conditions.news_sentiment}`);
        
        return parts.join('\n') || 'N/A';
    }

    setExpirationTimer(signalId, expiresAt, message) {
        const expirationTime = new Date(expiresAt);
        const timeUntilExpiration = expirationTime - new Date();

        if (timeUntilExpiration > 0) {
            setTimeout(async () => {
                try {
                    if (this.pendingSignals.has(signalId)) {
                        // Update message to show expired
                        const embed = EmbedBuilder.from(message.embeds[0])
                            .setColor(0x808080)
                            .setTitle(`⏰ Signal Expired: ${message.embeds[0].title.split(': ')[1]}`);

                        await message.edit({
                            embeds: [embed],
                            components: [] // Remove buttons
                        });

                        this.pendingSignals.delete(signalId);
                        logger.info(`Signal ${signalId} expired`);
                    }
                } catch (error) {
                    logger.error('Error handling signal expiration:', error);
                }
            }, timeUntilExpiration);
        }
    }

    async handlePositionUpdate(update) {
        try {
            if (update.type === 'position_closed') {
                await this.notifyPositionClosed(update);
            }
        } catch (error) {
            logger.error('Error handling position update:', error);
        }
    }

    async notifyPositionClosed(update) {
        try {
            const discordUserId = await this.getUserDiscordId(update.user_id);
            
            if (!discordUserId) return;

            const user = await this.client.users.fetch(discordUserId);
            
            if (!user) return;

            const pnlColor = update.realized_pnl >= 0 ? 0x00FF00 : 0xFF0000;
            const pnlEmoji = update.realized_pnl >= 0 ? '📈' : '📉';

            const embed = new EmbedBuilder()
                .setColor(pnlColor)
                .setTitle(`${pnlEmoji} Position Closed: ${update.symbol}`)
                .addFields(
                    { name: 'Strategy', value: update.strategy_type.replace('_', ' ').toUpperCase(), inline: true },
                    { name: 'Close Reason', value: update.close_reason.replace('_', ' ').toUpperCase(), inline: true },
                    { name: 'Exit Price', value: `$${update.exit_price}`, inline: true },
                    { name: 'Realized P&L', value: `$${update.realized_pnl.toFixed(2)}`, inline: true },
                    { name: 'P&L %', value: `${update.realized_pnl_pct.toFixed(2)}%`, inline: true }
                )
                .setTimestamp();

            await user.send({ embeds: [embed] });

            logger.info(`Position closed notification sent to user ${discordUserId}`);

        } catch (error) {
            logger.error('Error notifying position closed:', error);
        }
    }

    async getUserDiscordId(userId) {
        try {
            // Fetch from API or cache
            const response = await axios.get(`${this.apiUrl}/api/users/${userId}/discord`);
            return response.data.discord_user_id;
        } catch (error) {
            logger.error('Error fetching user Discord ID:', error);
            return null;
        }
    }

    async handleReaction(reaction, user, action) {
        // Legacy reaction handler - keeping for backwards compatibility
        // Modern implementation uses buttons instead
    }
}
