import enum


class LibEvents(enum.StrEnum):
    ON_MESSAGE = "chat.message.sent"
    ON_FOLLOW = "channel.followed"
    ON_SUBSCRIPTION = "channel.subscription.renewal"
    ON_SUBSCRIPTION_GIFT = "channel.subscription.gifts"
    ON_NEW_SUBSCRIPTION = "channel.subscription.new"
    ON_LIVESTREAM_UPDATED = "livestream.status.updated"
    ON_LIVESTREAM_METADATA_UPDATED = "livestream.metadata.updated"
    ON_MODERATION_BANNED = "moderation.banned"
    
    def __str__(self):
        return self.value

class Scopes(enum.StrEnum):
    USER_READ = "user:read"
    CHANNEL_READ = "channel:read"
    CHANNEL_WRITE = "channel:write"
    CHAT_WRITE = "chat:write"
    STREAMKEY_READ = "streamkey:read"
    EVENTS_SUBSCRIBE = "events:subscribe"
    MODERATION_BAN = "moderation:ban"
    
    def __str__(self):
        return self.value
