import { PrismaClient } from '@prisma/client';
import { LoaderFunctionArgs } from '@remix-run/cloudflare';
import { getPrismaClient } from './prisma';

export default function createLoader<LoaderReturnType>(
  loader: (args: LoaderFunctionArgs & { db: PrismaClient }) => LoaderReturnType
) {
  return (args: LoaderFunctionArgs) => {
    const prismaClient = getPrismaClient({ env: args.context.cloudflare.env });
    return loader({ ...args, db: prismaClient });
  };
}
