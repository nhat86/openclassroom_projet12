import { NextRequest, NextResponse } from 'next/server';
import { generateText } from 'ai';
import { google } from '@ai-sdk/google';
import { ALLOWED_TAGS } from '@/constants/tags.ts';
import { getClaimById, setClaimTag } from '@/database/queries.ts';

export async function POST(
  request: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  try {
    const { id } = await params;
    const claimId = parseInt(id);

    if (isNaN(claimId)) {
      return NextResponse.json({ error: 'Invalid claim ID' }, { status: 400 });
    }

    const claim = await getClaimById(claimId);
    if (!claim) {
      return NextResponse.json({ error: 'Claim not found' }, { status: 404 });
    }

    const labelsText = ALLOWED_TAGS.map((t) => `- ${t}`).join('\n');
    const prompt = `You are a text classification assistant specialized in consumer financial complaints.

Your task is to classify a consumer complaint into exactly one of the provided labels.

Rules:

- Read the complaint carefully.
- Select the single label that best matches the main issue described.
- Do not infer information that is not explicitly stated.
- If several issues are mentioned, prioritize the main reason for the complaint.
- You MUST pick your answer from the list below and copy it verbatim, even if another category would seem more accurate.
- If no label matches well, answer "Other financial services".
- Do not provide explanations or additional text.

Allowed categories:
${labelsText}

Consumer complaint:
<complaint>
${claim.content}
</complaint>

Output the exact category name from the list only.`;

    const { text } = await generateText({
      model: google('gemini-2.5-flash'),
      prompt,
    });

    const tag = text.trim();

    if (!ALLOWED_TAGS.includes(tag)) {
      return NextResponse.json(
        { error: `LLM returned an invalid tag: "${tag}"` },
        { status: 502 }
      );
    }

    await setClaimTag(claimId, tag);

    return NextResponse.json({ tag });
  } catch (error) {
    console.error('Error auto-tagging claim:', error);
    return NextResponse.json({ error: 'Failed to auto-tag claim' }, { status: 500 });
  }
}