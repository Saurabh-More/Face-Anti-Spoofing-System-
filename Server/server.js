const express = require('express');
const multer = require('multer');
const path = require('path');
const { exec } = require('child_process');
const fs = require('fs');

const app = express();
const PORT = 3000;

// Serve static files from public folder
app.use(express.static('public'));

// Parse JSON and form-data bodies (for camera blob upload)
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Create necessary folders if not exist
if (!fs.existsSync('uploads')) fs.mkdirSync('uploads');
if (!fs.existsSync('outputs')) fs.mkdirSync('outputs');

// Multer config for normal file uploads (video files)
const storage = multer.diskStorage({
  destination: 'uploads/',
  filename: (req, file, cb) => {
    cb(null, Date.now() + path.extname(file.originalname));
  }
});
const upload = multer({ storage });

// Upload and process route (for file input or camera blob)
app.post('/upload', upload.single('video'), (req, res) => {
  if (!req.file) {
    return res.status(400).send('No video file uploaded');
  }

  const inputPath = req.file.path;
  const outputPath = `outputs/output_${Date.now()}.mp4`;

  console.log(`Processing video: ${inputPath}`);

  exec(`python3 process_video.py "${inputPath}" "${outputPath}"`, (error, stdout, stderr) => {
    // Remove input file after processing
    fs.unlink(inputPath, () => { });

    if (error) {
      console.error(`Error processing video: ${error.message}`);
      console.error(stderr);
      return res.status(500).send('Error processing video');
    }

    console.log(`Video processed successfully: ${outputPath}`);

    // Extract Final Verdict from Python stdout
    const verdictMatch = stdout.match(/FINAL VERDICT: (.+)/);
    const verdict = verdictMatch ? verdictMatch[1] : "Unknown";
    console.log("Extracted Final Verdict:", verdict);

    res.setHeader("Content-Type", "video/mp4");
    res.setHeader("Content-Disposition", "inline");
    res.setHeader("X-Final-Verdict", verdict); // Add this header!

    const videoStream = fs.createReadStream(outputPath);
    videoStream.pipe(res);

    videoStream.on('close', () => {
      fs.unlink(outputPath, () => { });
    });

    videoStream.on('error', (err) => {
      console.error(`Error streaming video: ${err}`);
      res.status(500).send('Error streaming video');
    });
  });
});

app.listen(PORT, () => {
  console.log(`Server running at http://localhost:${PORT}`);
});
