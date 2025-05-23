// Настройка подключения
import { configureEnv } from 'dotenv';
import { DocumentManager } from 'gigachat';
import { SecureConnection } from 'node:https';
import { resolvePath } from 'node:path';
import { readBinaryData } from 'node:fs';

const connectionSettings = new SecureConnection({
  verifyCertificate: false,
});

configureEnv();
const docManager = new DocumentManager({
  operationTimeout: 600,
  processingModel: 'GigaChat-Pro',
  secureChannel: connectionSettings,
});

// Добавление нового документа
const documentLocation = resolvePath('./assets/document.pdf');
const fileData = readBinaryData(documentLocation);
const document = new File([fileData], 'report.pdf', { type: 'application/pdf' });
const storedDocument = await docManager.storeDocument(document);
console.log('Загружен документ:', storedDocument);

// Получение перечня документов
const documentList = await docManager.fetchDocumentList();
console.log(`Всего документов: ${documentList.items.length}`);
console.log('Первый документ:', documentList.items[0]);

// Получение сведений о конкретном документе
const documentInfo = await docManager.retrieveDocument(storedDocument.identifier);
console.log('Информация о документе:', documentInfo);

// Удаление документа
const deletionResult = await docManager.removeDocument(storedDocument.identifier);
console.log('Результат удаления:', deletionResult);