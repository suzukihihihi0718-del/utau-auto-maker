const lyrics = document.getElementById("lyrics");
const voicebank = document.getElementById("voicebank");
const makeButton = document.getElementById("makeButton");

const status = document.getElementById("status");
const voiceStatus = document.getElementById("voiceStatus");

const result = document.getElementById("result");
const info = document.getElementById("info");

const ustDownload =
  document.getElementById("ustDownload");

const wavDownload =
  document.getElementById("wavDownload");

const player =
  document.getElementById("player");


voicebank.addEventListener("change", () => {

  if (!voicebank.files.length) {
    voiceStatus.textContent =
      "UTAU音源ZIPを選択してください";
    return;
  }

  voiceStatus.textContent =
    "🎤 " +
    voicebank.files[0].name +
    " を選択しました";

});


makeButton.addEventListener("click", async () => {

  const text = lyrics.value.trim();

  if (!text) {
    alert("歌詞を入力してください！");
    return;
  }

  makeButton.disabled = true;

  status.textContent =
    "🎼 作曲しています……";

  result.style.display = "none";

  try {

    const form = new FormData();

    form.append("lyrics", text);

    if (voicebank.files.length) {
      form.append(
        "voicebank",
        voicebank.files[0]
      );
    }


    const response = await fetch(
      "/api/create",
      {
        method: "POST",
        body: form
      }
    );


    if (!response.ok) {

      const error =
        await response.text();

      throw new Error(error);
    }


    const data =
      await response.json();


    result.style.display = "block";


    info.innerHTML = `
      <p>🎵 BPM：${data.bpm}</p>
      <p>🎼 音符数：${data.notes}</p>
      <p>🎤 音源：${data.voicebank}</p>
    `;


    ustDownload.href =
      data.ust;


    if (data.wav) {

      wavDownload.style.display =
        "block";

      wavDownload.href =
        data.wav;

      player.src =
        data.wav;

    }


    status.textContent =
      "🎉 完成しました！";

  } catch (error) {

    console.error(error);

    status.textContent =
      "❌ エラー\n" +
      error.message;

  }


  makeButton.disabled = false;

});
