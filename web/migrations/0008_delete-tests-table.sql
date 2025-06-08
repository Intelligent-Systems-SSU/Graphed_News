-- DropTable
PRAGMA foreign_keys=off;
DROP TABLE "ABTest";
PRAGMA foreign_keys=on;

-- DropTable
PRAGMA foreign_keys=off;
DROP TABLE "tests";
PRAGMA foreign_keys=on;

-- RedefineTables
PRAGMA defer_foreign_keys=ON;
PRAGMA foreign_keys=OFF;
CREATE TABLE "new_TestSolve" (
    "id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    "testType" TEXT NOT NULL,
    "name" TEXT NOT NULL,
    "time" REAL,
    "correctAnswers" INTEGER
);
INSERT INTO "new_TestSolve" ("id", "name", "testType", "time") SELECT "id", "name", "testType", "time" FROM "TestSolve";
DROP TABLE "TestSolve";
ALTER TABLE "new_TestSolve" RENAME TO "TestSolve";
PRAGMA foreign_keys=ON;
PRAGMA defer_foreign_keys=OFF;
