const libshout = require("libshout");
const phin = require('phin');

const {exec} = require("child_process");
const fs = require("fs/promises");

function toSSTV(path, callback) {
	exec(`python3 -m pysstv --mode Robot36 ${path} temp.wav`, async (err, stdout, stderr) => {
		if(err) throw err;

		console.log("[INFO] Sucesfully converted to SSTV")

		exec(`ffmpeg -y -i temp.wav -acodec libvorbis temp.ogg`, async(err) => {
			if(err) throw err;

			console.log("[INFO] Sucesfully converted WAV to OGG")

			await fs.unlink("temp.wav");

			callback();
		});

	});

}


async function run() {
    const shout = new libshout();

	shout.setHost('');
    shout.setProtocol(0);
    shout.setPort();

    shout.setUser('source');
	shout.setPassword('');

	shout.setMount('/yourfriend-ksic');
	shout.setFormat(0);

	shout.open();

	async function sendNewSSTV() {
		const imageRequest = await phin({
			url: "https://picsum.photos/320/240",
			followRedirects: true
		})

		await fs.writeFile("temp.jpg", imageRequest.body);

		toSSTV("temp.jpg", async () => {
			const fd = await fs.open('temp.ogg', 'r');
			const tmp = Buffer.allocUnsafe(1024 * 4);
			
			while(1) {
				const {bytesRead} = await fd.read(tmp, 0, tmp.byteLength, null);
				
				if(bytesRead) {
					shout.send(tmp.buffer.slice(0, bytesRead));
				} else {
					console.log("end")

					await fd?.close();

					await sendNewSSTV()
					break;
				}
				shout.sync();
			}
		})
	}

	sendNewSSTV()
}
process.on("SIGINT", async () => {
	console.log("[INFO] Shutting down..");
	await fs.unlink("temp.jpg");
	await fs.unlink("temp.ogg");
	process.exit();
});
  
run();