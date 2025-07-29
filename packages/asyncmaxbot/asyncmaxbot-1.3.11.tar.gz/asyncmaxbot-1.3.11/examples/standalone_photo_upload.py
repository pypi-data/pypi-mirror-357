import asyncio
import json
from maxbot.bot import Bot

TOKEN = open('token.txt').read().strip()

async def main():
    bot = Bot(TOKEN)
    async with bot:
        print('Бот запущен. Жду вложения...')
        while True:
            updates = await bot.get_updates(limit=1, timeout=60)
            for upd in updates.get('updates', []):
                msg = upd.get('message')
                if not msg:
                    continue
                attachments = msg.get('body', {}).get('attachments', [])
                if not attachments:
                    continue
                for att in attachments:
                    print('Вложение:', json.dumps(att, ensure_ascii=False, indent=2))
                    # Сохраняем структуру для анализа
                    with open('last_attachment.json', 'w', encoding='utf-8') as f:
                        json.dump(att, f, ensure_ascii=False, indent=2)
                    # Валидация
                    if 'type' not in att:
                        print('❌ Нет type во вложении!')
                        continue
                    if 'payload' not in att:
                        print('❌ Нет payload во вложении!')
                        continue
                    payload = att['payload']
                    if not isinstance(payload, dict):
                        print('❌ payload не dict!')
                        continue
                    print(f'✅ Тип вложения: {att["type"]}, payload: {payload}')
            await asyncio.sleep(1)

if __name__ == '__main__':
    asyncio.run(main()) 