import { PrismaClient } from '@prisma/client';
import { ActionFunctionArgs } from '@remix-run/cloudflare';

import { getPrismaClient } from 'app/utils/prisma';

export default function createAction<ActionReturnType>(
  loader: (args: ActionFunctionArgs & { db: PrismaClient }) => ActionReturnType
) {
  return (args: ActionFunctionArgs) => {
    const prismaClient = getPrismaClient({ env: args.context.cloudflare.env });
    return loader({ ...args, db: prismaClient });
  };
}
