/**
 * Anti-duplication lint: Detect redundant lessons across projects/memory.
 */

import fs from 'fs';
import path from 'path';
import { promisify } from 'util';
import { SequenceMatcher } from 'difflib';

const readFile = promisify(fs.readFile);
const readdir = promisify(fs.readdir);

// Types
interface Lesson {
  id: string;
  text: string;
  sourceFile?: string;
  type?: "principle" | "pitfall";
}

interface DuplicateGroup {
  canonicalId: string;
  canonicalText: string;
  duplicates: Lesson[];
  similarityScores: number[];
  type: string;
}

/**
 * Anti-duplication lint class for detecting redundant lessons.
 */
export class AntiDuplicationLint {
  private threshold: number;

  constructor(similarityThreshold: number = 0.75) {
    this.threshold = similarityThreshold;
  }

  async checkExtraction(extractionFile: string): Promise<DuplicateGroup[]> {
    const data = JSON.parse(await readFile(extractionFile, 'utf-8'));
    const lessons: Lesson[] = data.lessons;
    return this.findDuplicates(lessons);
  }

  async checkMemory(memoryDir: string): Promise<DuplicateGroup[]> {
    const allLessons: Lesson[] = [];
    const files = await readdir(memoryDir);

    for (const fileName of files) {
      if (fileName.endsWith('.md')) {
        const filePath = path.join(memoryDir, fileName);
        const content = await readFile(filePath, 'utf-8');

        content.split('\n').forEach(line => {
          if (line.startsWith('- ✓') || line.startsWith('- ❌')) {
            const text = line.trim();
            allLessons.push({
              id: `${fileName}_${this.hash(text)}`,
              text,
              sourceFile: fileName,
              type: line.includes('✓') ? 'principle' : 'pitfall',
            });
          }
        });
      }
    }

    return this.findDuplicates(allLessons);
  }

  private findDuplicates(lessons: Lesson[]): DuplicateGroup[] {
    const duplicates: DuplicateGroup[] = [];
    const seenIds: Set<string> = new Set();

    for (let i = 0; i < lessons.length; i++) {
      const lesson1 = lessons[i];
      if (seenIds.has(lesson1.id)) continue;

      const similar: { lesson: Lesson; ratio: number }[] = [];
      for (let j = i + 1; j < lessons.length; j++) {
        const lesson2 = lessons[j];
        if (seenIds.has(lesson2.id)) continue;

        const ratio = this.similarity(lesson1.text, lesson2.text);
        if (ratio >= this.threshold) {
          similar.push({ lesson: lesson2, ratio });
          seenIds.add(lesson2.id);
        }
      }

      if (similar.length > 0) {
        seenIds.add(lesson1.id);
        duplicates.push({
          canonicalId: lesson1.id,
          canonicalText: lesson1.text,
          duplicates: similar.map(s => s.lesson),
          similarityScores: similar.map(s => s.ratio),
          type: lesson1.type || "unknown",
        });
      }
    }

    return duplicates;
  }

  private similarity(text1: string, text2: string): number {
    const s1 = text1.toLowerCase().trim();
    const s2 = text2.toLowerCase().trim();
    const matcher = new SequenceMatcher(null, s1, s2);
    return matcher.ratio();
  }

  private hash(text: string): string {
    let hash = 0;
    for (let i = 0; i < text.length; i++) {
      const char = text.charCodeAt(i);
      hash = (hash << 5) - hash + char;
      hash |= 0; // Convert to 32bit integer
    }
    return hash.toString();
  }

  report(duplicates: DuplicateGroup[], verbose = false): string {
    if (duplicates.length === 0) return '✓ No duplicates found';

    const lines: string[] = [`\n⚠️  Found ${duplicates.length} duplicate groups:\n`];
    for (const [i, group] of duplicates.entries()) {
      lines.push(`${i + 1}. CANONICAL: ${group.canonicalText.slice(0, 60)}...`);
      lines.push(`   Type: ${group.type}`);
      lines.push(`   Duplicates (${group.duplicates.length}):`);
      group.duplicates.forEach((dup, idx) => {
        lines.push(`     - [${(group.similarityScores[idx] * 100).toFixed(1)}%] ${dup.text.slice(0, 60)}...`);
        lines.push(`       From: ${dup.sourceFile || 'unknown'}`);
      });
      lines.push('');
    }
    lines.push('RECOMMENDATION: Merge duplicates into single lesson before promotion');

    return lines.join('\n');
  }
}

export const cmdLint = async (args: {
  extractionFile?: string;
  memoryDir?: string;
  threshold: number;
  verbose: boolean;
}): Promise<number | null> => {
  const lint = new AntiDuplicationLint(args.threshold);

  if (args.extractionFile) {
    const extractionFile = args.extractionFile;
    if (!fs.existsSync(extractionFile)) {
      console.error(`Error: ${extractionFile} not found`);
      return null;
    }

    const duplicates = await lint.checkExtraction(extractionFile);
    console.log(lint.report(duplicates, args.verbose));
    return duplicates.length;
  } else if (args.memoryDir) {
    const memoryDir = args.memoryDir;
    if (!fs.existsSync(memoryDir) || !fs.statSync(memoryDir).isDirectory()) {
      console.error(`Error: ${memoryDir} is not a directory`);
      return null;
    }

    const duplicates = await lint.checkMemory(memoryDir);
    console.log(lint.report(duplicates, args.verbose));
    return duplicates.length;
  } else {
    console.error('Error: Specify --extractionFile or --memoryDir');
    return null;
  }
};