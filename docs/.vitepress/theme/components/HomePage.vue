<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
import { withBase } from 'vitepress'
import { home } from '../home'
import Icon from './Icon.vue'

const category = ref('全部')
const categories = ['全部', '开发笔记', '部署实践']
const notes = computed(() => home.notes.filter(n => category.value === '全部' || n.category === category.value))
const menuOpen = ref(false)
const commandOpen = ref(false)
const query = ref('')
const searchInput = ref<HTMLInputElement>()
const commandPanel = ref<HTMLElement>()
const activeResult = ref(0)
const phase = ref(1)
const phases = ['灵感', '构建', '分享']
const href = (url: string) => url.startsWith('/') ? withBase(url) : url
const commands = computed(() => [
  { title: '探索项目', href: '#projects', group: '页面', icon: 'code' },
  { title: '浏览全部笔记', href: '#notes', group: '页面', icon: 'book' },
  { title: '关于这个空间', href: '#about', group: '页面', icon: 'sun' },
  ...home.notes.map(n => ({ title: n.title, href: n.href, group: n.category, icon: 'book' })),
  { title: 'GitHub · PengJiang23', href: home.github, group: '外部链接', icon: 'arrow' },
].filter(c => `${c.title}${c.group}`.toLowerCase().includes(query.value.toLowerCase())))
let previousFocus: HTMLElement | null = null
async function openCommand() {
  previousFocus = document.activeElement as HTMLElement
  menuOpen.value = false
  query.value = ''
  activeResult.value = 0
  commandOpen.value = true
  document.body.style.overflow = 'hidden'
  await nextTick()
  searchInput.value?.focus()
}
function closeCommand() {
  commandOpen.value = false
  document.body.style.overflow = ''
  previousFocus?.focus()
}
function choose(url: string) {
  closeCommand()
  if (url.startsWith('https:')) window.open(url, '_blank', 'noopener,noreferrer')
  else window.location.assign(href(url))
}
function onKey(event: KeyboardEvent) {
  if ((event.metaKey || event.ctrlKey) && event.key.toLowerCase() === 'k') {
    event.preventDefault()
    commandOpen.value ? closeCommand() : openCommand()
  }
  if (event.key === 'Escape') { if (commandOpen.value) closeCommand(); menuOpen.value = false }
  if (!commandOpen.value) return
  if (event.key === 'ArrowDown' || event.key === 'ArrowUp') {
    event.preventDefault()
    const count = commands.value.length
    if (count) activeResult.value = (activeResult.value + (event.key === 'ArrowDown' ? 1 : -1) + count) % count
    nextTick(() => document.getElementById(`command-${activeResult.value}`)?.scrollIntoView({ block: 'nearest' }))
  }
  if (event.key === 'Enter' && commands.value[activeResult.value] && document.activeElement === searchInput.value) {
    event.preventDefault()
    choose(commands.value[activeResult.value].href)
  }
  if (event.key === 'Tab') {
    const items = commandPanel.value?.querySelectorAll<HTMLElement>('input, button, a')
    if (!items?.length) return
    const first = items[0], last = items[items.length - 1]
    if (event.shiftKey && document.activeElement === first) { event.preventDefault(); last.focus() }
    else if (!event.shiftKey && document.activeElement === last) { event.preventDefault(); first.focus() }
  }
}
onMounted(() => window.addEventListener('keydown', onKey))
onUnmounted(() => { window.removeEventListener('keydown', onKey); document.body.style.overflow = '' })
</script>

<template>
  <div class="jf-home" id="top">
    <a class="jf-skip" href="#main">跳到内容</a>
    <header class="jf-header">
      <a class="jf-brand" :href="withBase('/')" aria-label="JFred 首页"><span class="jf-mark"><i></i><i></i><i></i></span>JFred<span class="jf-brand-dot">.</span></a>
      <nav class="jf-nav" aria-label="主导航"><a href="#projects">项目</a><a href="#notes">笔记</a><a href="#about">关于</a></nav>
      <div class="jf-header-actions"><button class="jf-search" @click="openCommand" aria-label="打开快捷导航"><Icon name="search" :size="16" /><span>快捷导航</span><kbd>⌘ K</kbd></button><a class="jf-github" :href="home.github" target="_blank" rel="noopener noreferrer">GitHub <Icon name="arrow" :size="15" /></a><button class="jf-mobile-toggle" @click="menuOpen = !menuOpen" :aria-expanded="menuOpen" aria-label="切换导航菜单"><Icon :name="menuOpen ? 'close' : 'menu'" /></button></div>
      <nav v-if="menuOpen" class="jf-mobile-nav" aria-label="移动端导航"><a v-for="item in [['项目', '#projects'], ['笔记', '#notes'], ['关于', '#about']]" :href="item[1]" @click="menuOpen = false">{{ item[0] }}<Icon name="right" /></a><button @click="openCommand">快捷导航<Icon name="search" /></button></nav>
    </header>

    <main id="main">
      <section class="jf-hero jf-wrap" aria-labelledby="hero-heading">
        <div class="jf-hero-copy"><div class="jf-eyebrow"><span class="jf-live-dot"></span> A SMALL CORNER OF THE INTERNET</div>
          <h1 id="hero-heading">{{ home.headline[0] }}<br><span>{{ home.headline[1] }}</span></h1>
          <p class="jf-intro">{{ home.description }}</p>
          <div class="jf-hero-actions"><a class="jf-button jf-button-primary" href="#projects">探索我的作品 <Icon name="right" :size="18" /></a><a class="jf-text-link" href="#notes">读一点新东西 <Icon name="arrow" :size="16" /></a></div>
          <div class="jf-hero-note"><span class="jf-avatar">P<span></span></span><div><strong>保持好奇，持续构建。</strong><span>CODE · CREATE · SHARE</span></div></div>
        </div>
        <div class="jf-playground" aria-label="从灵感到分享的交互演示">
          <div class="jf-art-grid"></div><div class="jf-orb"><span></span></div><div class="jf-orbit jf-orbit-one"></div><div class="jf-orbit jf-orbit-two"></div><span class="jf-floating-dot"></span>
          <div class="jf-art-label"><span></span> THE CREATIVE PROCESS <span>↗</span></div>
          <div class="jf-preview">
            <div class="jf-window-bar"><span class="jf-window-dots"><i></i><i></i><i></i></span><span>workspace / {{ ['a-new-idea', 'building-something', 'ready-to-share'][phase] }}</span><Icon name="code" :size="14" /></div>
            <div class="jf-preview-body" :key="phase">
              <template v-if="phase === 0"><div class="jf-preview-kicker">EVERYTHING STARTS HERE</div><h3>一个小小的想法<span>✳</span></h3><p>如果把零散的笔记，<br>变成一个可以探索的空间呢？</p><div class="jf-idea-tags"><span>好奇心</span><span>一点灵感</span><span>无限可能</span></div></template>
              <template v-else-if="phase === 1"><div class="jf-preview-kicker">FROM THOUGHT TO THING</div><div class="jf-code"><div><em>01</em><span class="jf-code-purple">const</span> idea = <span class="jf-code-green">'something new'</span></div><div><em>02</em><span class="jf-code-purple">await</span> build(idea)</div><div><em>03</em>share(<span class="jf-code-blue">withTheWorld</span>)<span class="jf-cursor"></span></div></div><div class="jf-build-status"><span class="jf-check"><Icon name="check" :size="12" /></span> 让想法，慢慢成形。<span>building</span></div></template>
              <template v-else><div class="jf-preview-kicker">MADE TO BE SHARED</div><h3>让灵感，继续生长。<span>↗</span></h3><p>记录过程，分享所得。<br>下一个想法，可能就从这里开始。</p><a :href="href('/notes/workflow')" class="jf-preview-link">看看我的更新流程 <Icon name="right" :size="15" /></a></template>
            </div>
          </div>
          <div class="jf-phase-tabs" role="tablist" aria-label="创作阶段"><button v-for="(label, index) in phases" :key="label" role="tab" :aria-selected="phase === index" :class="{ active: phase === index }" @click="phase = index"><span>0{{ index + 1 }}</span>{{ label }}</button></div>
          <div class="jf-art-caption">A little curiosity. A little code. A new possibility.</div>
        </div>
      </section>
      <div class="jf-principles jf-wrap"><span>从好奇心出发</span><div><span><Icon name="code" :size="17" />用代码探索</span><span><Icon name="book" :size="17" />用文字沉淀</span><span><Icon name="sun" :size="17" />把过程分享</span></div><span class="jf-principles-end">ALWAYS A WORK IN PROGRESS ↗</span></div>

      <section id="projects" class="jf-section jf-wrap" aria-labelledby="projects-title"><div class="jf-section-heading"><div><span class="jf-section-label">01 / SELECTED WORK</span><h2 id="projects-title">不止想想，也动手做。</h2><p>一些正在构建的东西，和背后的实践。</p></div><a class="jf-text-link" :href="home.github" target="_blank" rel="noopener noreferrer">在 GitHub 继续探索 <Icon name="arrow" :size="16" /></a></div>
        <div class="jf-project-grid"><a v-for="project in home.projects" :key="project.title" class="jf-project-card" :href="href(project.href)" :target="project.href.startsWith('https') ? '_blank' : undefined" rel="noopener noreferrer">
          <div class="jf-project-art" :class="`jf-project-art-${project.visual}`">
            <template v-if="project.visual === 'website'"><div class="jf-mini-browser"><div class="jf-mini-nav"><strong>JFred.</strong><span>Ideas. Notes. Things.</span><Icon name="arrow" :size="13" /></div><div class="jf-mini-page"><span>A PERSONAL SPACE</span><strong>Stay curious.<br>Keep building<span>✳</span></strong><div class="jf-mini-lines"><i></i><i></i></div><div class="jf-mini-blocks"><i></i><i></i><i></i></div></div></div><span class="jf-art-sticker"><span>✳</span> MADE WITH CURIOSITY</span></template>
            <template v-else><div class="jf-pipeline"><div><span class="jf-pipeline-icon"><Icon name="code" :size="23" /></span><strong>Code</strong><small>一个新的想法</small></div><i></i><div><span class="jf-pipeline-icon"><svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.4" aria-hidden="true"><path d="m12 3 9 5-9 5-9-5 9-5Zm-9 5v9l9 5 9-5V8M12 13v9"/></svg></span><strong>Build</strong><small>自动构建镜像</small></div><i></i><div><span class="jf-pipeline-icon"><Icon name="arrow" :size="23" /></span><strong>Live</strong><small>让世界看见</small></div></div><span class="jf-pipeline-caption"><span class="jf-live-dot"></span> 小小的提交，完整的旅程。</span></template>
          </div>
          <div class="jf-project-content"><span class="jf-section-label">{{ project.category }}</span><h3>{{ project.title }}<Icon name="arrow" :size="22" /></h3><p>{{ project.description }}</p><div class="jf-project-bottom"><div class="jf-tags"><span v-for="tag in project.stack">{{ tag }}</span></div><span class="jf-project-action">{{ project.action }}</span></div></div>
        </a></div>
      </section>

      <section id="notes" class="jf-notes-section" aria-labelledby="notes-title"><div class="jf-wrap"><div class="jf-section-heading"><div><span class="jf-section-label">02 / FIELD NOTES</span><h2 id="notes-title">边探索，边记录。</h2><p>把走过的路，变成下一次出发的地图。</p></div><div class="jf-filters" role="group" aria-label="筛选笔记"><button v-for="item in categories" :aria-pressed="category === item" :class="{ active: category === item }" @click="category = item">{{ item }}</button></div></div>
          <div class="jf-notes-grid" aria-live="polite"><a v-for="note in notes" :key="note.href" :href="href(note.href)" class="jf-note-card"><div class="jf-note-top"><span class="jf-note-symbol" :class="note.color"><Icon :name="note.tag === 'DEPLOYMENT' ? 'arrow' : note.tag === 'VITEPRESS' ? 'code' : 'book'" :size="21" /></span><span>{{ note.tag }}</span><Icon name="arrow" :size="19" /></div><h3>{{ note.title }}</h3><p>{{ note.description }}</p><div class="jf-note-meta"><span>{{ note.category }}</span><span>{{ note.read }} <Icon name="right" :size="14" /></span></div></a></div>
        </div></section>

      <section id="about" class="jf-about jf-wrap" aria-labelledby="about-title"><div class="jf-about-left"><span class="jf-section-label">03 / A LITTLE ABOUT ME</span><h2 id="about-title">持续记录，<br>也持续构建<span>。</span></h2></div><div class="jf-about-right"><p>我是 PengJiang，喜欢折腾技术，也享受把事情做出来的过程。</p><p>这个空间装着我的学习笔记、项目实践和偶尔冒出来的想法。它不需要一次就完美，重要的是，一直在向前。</p><a class="jf-text-link" :href="home.github" target="_blank" rel="noopener noreferrer">来 GitHub 找我 <Icon name="arrow" :size="17" /></a><div class="jf-about-signature">A place to think, make & grow.</div></div></section>
    </main>
    <footer class="jf-footer jf-wrap"><div><a class="jf-brand" href="#top">JFred<span class="jf-brand-dot">.</span></a><span>一个想法，下一种可能。</span></div><span>© {{ new Date().getFullYear() }} {{ home.author }}</span><a href="#top">回到顶部 <span>↑</span></a></footer>

    <Teleport to="body"><div v-if="commandOpen" class="jf-command-overlay" @click.self="closeCommand"><section class="jf-command" ref="commandPanel" role="dialog" aria-modal="true" aria-labelledby="command-title"><h2 id="command-title" class="jf-sr-only">快捷导航</h2><div class="jf-command-input"><Icon name="search" /><input ref="searchInput" v-model="query" @input="activeResult = 0" placeholder="想去哪里？搜索页面或笔记…" aria-label="搜索页面或笔记" aria-controls="command-results" /><button @click="closeCommand" aria-label="关闭快捷导航">Esc</button></div><div class="jf-command-results" id="command-results"><span class="jf-command-label">{{ query ? '搜索结果' : '探索这个空间' }}</span><button v-for="(command, index) in commands" :id="`command-${index}`" :class="{ active: index === activeResult }" @mouseenter="activeResult = index" @click="choose(command.href)"><Icon :name="command.icon" :size="18" /><span>{{ command.title }}<small>{{ command.group }}</small></span><Icon name="enter" :size="16" /></button><p v-if="!commands.length" class="jf-no-results">没有找到相关内容，换一个关键词试试。</p></div><div class="jf-command-footer"><span><kbd>↑</kbd><kbd>↓</kbd> 选择</span><span><kbd>↵</kbd> 前往</span><span>JFred / 快捷导航</span></div></section></div></Teleport>
  </div>
</template>
