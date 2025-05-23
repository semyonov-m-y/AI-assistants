import { GigaAI } from 'giga-ai-sdk';
import * as env from 'environment-config';
import { SecureAgent } from 'node:https';

// Инициализация окружения
env.configure();

const securityAgent = new SecureAgent({
    verifyCertificates: false,
});

const aiClient = new GigaAI({
    requestTimeout: 800,
    aiModel: 'GigaAI-Pro',
    securityAgent: securityAgent,
});

// Сообщения системы
import { ConversationMessage } from 'giga-ai-sdk/interfaces';
const conversationHistory: ConversationMessage[] = [
  {
    role: 'system',
    content: `Ты цифровой ассистент супермаркета "Гурман". 
    Твои возможности:
      fetch_inventory: Получает текущий ассортимент товаров
      retrieve_item_details: Получает детализацию по конкретным товарам
    Ты можешь комбинировать запросы для комплексных ответов
    Будь вежлив и предлагай дополнительные варианты`,
  },
];

// Расширенная база данных продуктов
const MARKET_INVENTORY = [
    {
        productName: 'Молоко "Деревенское" 3.2%',
        cost: 89,
        stock: 15,
        productId: 1001,
        category: 'Молочные продукты'
    },
    {
        productName: 'Хлеб "Бородинский"',
        cost: 65,
        stock: 8,
        productId: 1002,
        category: 'Хлебобулочные изделия'
    },
    {
        productName: 'Сыр "Гауда"',
        cost: 350,
        stock: 12,
        productId: 1003,
        category: 'Молочные продукты'
    },
    {
        productName: 'Масло сливочное "Вологодское"',
        cost: 220,
        stock: 18,
        productId: 1004,
        category: 'Молочные продукты'
    },
    {
        productName: 'Яйца куриные С0',
        cost: 120,
        stock: 25,
        productId: 1005,
        category: 'Яйца'
    },
    {
        productName: 'Кофе молотый "Jacobs"',
        cost: 450,
        stock: 7,
        productId: 1006,
        category: 'Бакалея'
    },
    {
        productName: 'Чай "Greenfield"',
        cost: 180,
        stock: 14,
        productId: 1007,
        category: 'Бакалея'
    },
    {
        productName: 'Сахар-песок',
        cost: 95,
        stock: 22,
        productId: 1008,
        category: 'Бакалея'
    },
];

// Функциональные возможности
function fetchCurrentInventory(): any {
  console.log('Активирована функция: fetchCurrentInventory');
  return MARKET_INVENTORY.map((item) => {
    return { 
      title: item.productName, 
      identifier: item.productId,
      group: item.category
    };
  });
}

function getDetailedProductData(params: any) {
  console.log('Активирована функция: getDetailedProductData');
  console.log(`Параметры запроса: ${JSON.stringify(params)}`);
  return MARKET_INVENTORY.filter((product) => 
    params.productIdentifiers.includes(product.productId)
  ).map(item => ({
    itemName: item.productName,
    itemId: item.productId,
    available: item.stock,
    price: item.cost,
    type: item.category
  }));
}

const availableOperations = [
  {
    operationName: 'fetch_inventory',
    description: 'Получает список доступных товаров в магазине',
    inputParams: {
      type: 'object',
      properties: {
        filter: {
          type: 'string',
          description: 'Фильтр по категории'
        },
      },
    },
    outputStructure: {
      type: 'object',
      properties: {
        items: {
          type: 'array',
          items: {
            type: 'object',
            properties: {
              title: {
                type: 'string',
                description: 'Наименование товара',
              },
              identifier: {
                type: 'number',
                description: 'Уникальный код товара',
              },
              group: {
                type: 'string',
                description: 'Категория товара',
              },
            },
          },
        },
      },
    },
  },
  {
    operationName: 'retrieve_item_details',
    description: 'Получает детальную информацию о запрошенных товарах',
    inputParams: {
      type: 'object',
      properties: {
        productIdentifiers: {
          type: 'array',
          items: {
            type: 'number',
            description: 'Коды товаров',
          },
        },
      },
    },
    outputStructure: {
      type: 'object',
      properties: {
        products: {
          type: 'array',
          items: {
            type: 'object',
            properties: {
              itemName: {
                type: 'string',
                description: 'Полное название',
              },
              itemId: {
                type: 'number',
                description: 'Идентификатор',
              },
              available: {
                type: 'number',
                description: 'Доступное количество',
              },
              price: {
                type: 'number',
                description: 'Цена за единицу',
              },
              type: {
                type: 'string',
                description: 'Категория товара',
              },
            },
          },
        },
      },
    },
  },
];

// Диалоговая система
async function handleCustomerInteraction() {
  let customerQuery = prompt('Ваш запрос: ');
  while (customerQuery) {
    console.log(`Клиент: ${customerQuery}`)
    conversationHistory.push({
        role: 'user',
        content: customerQuery,
    });
    
    let aiResponse = await aiClient.dialogue({
        operations: availableOperations,
        conversation: conversationHistory,
        operationSelection: "smart"
    });
    
    if (aiResponse.selections[0]?.message) {
      conversationHistory.push(aiResponse.selections[0].message);
    }
    
    if (aiResponse.selections[0]?.message.operationRequest) {
        let operationResult: any = {};
        switch (aiResponse.selections[0].message.operationRequest.name) {
            case 'fetch_inventory':
                operationResult = fetchCurrentInventory();
                break;
            case 'retrieve_item_details':
                operationResult = getDetailedProductData(
                  aiResponse.selections[0].message.operationRequest.parameters
                );
                break;
        }
        
        conversationHistory.push({
            role: 'operation',
            content: JSON.stringify(operationResult),
        });
        
        aiResponse = await aiClient.dialogue({
            operations: availableOperations,
            conversation: conversationHistory,
        });
    }
    
    console.log(`Ассистент: ${aiResponse.selections[0]?.message.content}`)
    customerQuery = prompt('Ваш запрос: ');
  }
}

// Запуск диалога
handleCustomerInteraction().catch(console.error);