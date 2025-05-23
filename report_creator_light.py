import GigaChat from 'gigachat';
import * as dotenv from 'dotenv';
import { Agent } from 'node:https';

dotenv.config();

const httpsAgent = new Agent({
    rejectUnauthorized: false,
});

const client = new GigaChat({
    profanityCheck: false,
    timeout: 600,
    model: 'GigaChat-Pro',
    httpsAgent: httpsAgent,
});

let message = "";
for await (const chunk of client.stream('Напиши отчет на тему ипотечного кредитования')) {
    message += chunk.choices[0]?.delta.content;
}
message