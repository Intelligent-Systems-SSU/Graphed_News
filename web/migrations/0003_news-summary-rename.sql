-- DropTable
PRAGMA foreign_keys=off;
DROP TABLE "NewsSummmary";
PRAGMA foreign_keys=on;

-- CreateTable
CREATE TABLE "NewsSummary" (
    "id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    "newsId" INTEGER NOT NULL,
    "summary" TEXT NOT NULL,
    CONSTRAINT "NewsSummary_newsId_fkey" FOREIGN KEY ("newsId") REFERENCES "News" ("id") ON DELETE RESTRICT ON UPDATE CASCADE
);

-- CreateIndex
CREATE UNIQUE INDEX "NewsSummary_newsId_key" ON "NewsSummary"("newsId");
