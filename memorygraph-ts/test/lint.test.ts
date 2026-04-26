import { AntiDuplicationLint } from '../src/lint';
import path from 'path';
import fs from 'fs';
import os from 'os';

const tempDir = fs.mkdtempSync(path.join(os.tmpdir(), 'lint-test-'));
const writeTempFile = (fileName: string, content: string): string => {
  const filePath = path.join(tempDir, fileName);
  fs.writeFileSync(filePath, content);
  return filePath;
};

describe('AntiDuplicationLint', () => {
  const lint = new AntiDuplicationLint(0.8);

  afterAll(() => {
    fs.rmSync(tempDir, { recursive: true, force: true });
  });

  it('should find no duplicates for unique lessons in extraction', async () => {
    const extractionData = {
      lessons: [
        { id: '1', text: 'Lesson A' },
        { id: '2', text: 'Lesson B' },
        { id: '3', text: 'Lesson C' },
      ],
    };
    const filePath = writeTempFile('unique_extraction.json', JSON.stringify(extractionData));

    const duplicates = await lint.checkExtraction(filePath);
    expect(duplicates).toHaveLength(0);
  });

  it('should detect duplicates in extraction data', async () => {
    const extractionData = {
      lessons: [
        { id: '1', text: 'Lesson A' },
        { id: '2', text: 'Lesson A slightly modified' },
        { id: '3', text: 'Completely different lesson' },
      ],
    };
    const filePath = writeTempFile('duplicate_extraction.json', JSON.stringify(extractionData));

    const duplicates = await lint.checkExtraction(filePath);
    expect(duplicates).toHaveLength(1);
    expect(duplicates[0].duplicates).toHaveLength(1);
    expect(duplicates[0].canonicalText).toBe('Lesson A');
  });

  it('should find no duplicates for unique lessons in memory', async () => {
    writeTempFile('file1.md', '- ✓ Unique lesson A\n- ❌ Unique pitfall A');
    writeTempFile('file2.md', '- ✓ Unique lesson B\n- ❌ Unique pitfall B');

    const duplicates = await lint.checkMemory(tempDir);
    expect(duplicates).toHaveLength(0);
  });

  it('should detect duplicates across memory files', async () => {
    writeTempFile('file1.md', '- ✓ Repeated lesson\n- ❌ Unique pitfall');
    writeTempFile('file2.md', '- ✓ Repeated lesson with slight change\n- ❌ Another unique pitfall');

    const duplicates = await lint.checkMemory(tempDir);
    expect(duplicates).toHaveLength(1);
    expect(duplicates[0].duplicates).toHaveLength(1);
    expect(duplicates[0].canonicalText).toBe('Repeated lesson');
  });

  it('should report correctly with verbose mode', async () => {
    const extractionData = {
      lessons: [
        { id: '1', text: 'Lesson A' },
        { id: '2', text: 'Lesson A slightly modified' },
        { id: '3', text: 'Another lesson completely different' },
      ],
    };
    const filePath = writeTempFile('verbose_report.json', JSON.stringify(extractionData));

    const duplicates = await lint.checkExtraction(filePath);
    const report = lint.report(duplicates, true);

    expect(report).toContain('⚠️');
    expect(report).toContain('Lesson A');
    expect(report).toContain('Lesson A slightly modified');
  });
});