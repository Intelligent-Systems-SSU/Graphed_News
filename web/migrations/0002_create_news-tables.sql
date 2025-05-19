-- CreateTable
CREATE TABLE "News" (
    "id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    "url" TEXT NOT NULL,
    "title" TEXT NOT NULL,
    "content" TEXT NOT NULL,
    "created_at" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" DATETIME NOT NULL
);

-- CreateTable
CREATE TABLE "NewsSummmary" (
    "id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    "newsId" INTEGER NOT NULL,
    "summary" TEXT NOT NULL,
    CONSTRAINT "NewsSummmary_newsId_fkey" FOREIGN KEY ("newsId") REFERENCES "News" ("id") ON DELETE RESTRICT ON UPDATE CASCADE
);

-- CreateTable
CREATE TABLE "NewsKeyword" (
    "id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    "newsId" INTEGER NOT NULL,
    "keyword" TEXT NOT NULL,
    "description" TEXT NOT NULL,
    CONSTRAINT "NewsKeyword_newsId_fkey" FOREIGN KEY ("newsId") REFERENCES "News" ("id") ON DELETE RESTRICT ON UPDATE CASCADE
);

-- CreateIndex
CREATE UNIQUE INDEX "NewsSummmary_newsId_key" ON "NewsSummmary"("newsId");

-- CreateIndex
CREATE UNIQUE INDEX "NewsKeyword_newsId_key" ON "NewsKeyword"("newsId");
