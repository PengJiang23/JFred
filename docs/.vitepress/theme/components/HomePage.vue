<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
import { withBase } from 'vitepress'
import { home } from '../home'
import { topics } from '../content'
import HeatCount from './HeatCount.vue'
import PublicStats from './PublicStats.vue'
import Icon from './Icon.vue'

const category = ref('全部')
const categories = ['全部', 'AI 学习', '理财笔记', '兴趣档案', '工程实践']
const notes = computed(() => home.notes.filter(n => category.value === '全部' || n.category === category.value))
const menuOpen = ref(false)
const commandOpen = ref(false)
const query = ref('')
const searchInput = ref<HTMLInputElement>()
const commandPanel = ref<HTMLElement>()
const activeResult = ref(0)
const phase = ref(0)
const phases = ['AI 学习', '理财', '兴趣']
const href = (url: string) => url.startsWith('/') ? withBase(url) : url
const commands = computed(() => [
  { title: '浏览专题目录', href: '/topics/', group: '页面', icon: 'code' },
  { title: '浏览全部笔记', href: '#notes', group: '页面', icon: 'book' },
  { title: '关于这个空间', href: '#about', group: '页面', icon: 'sun' },
  ...topics.flatMap(t => t.chapters.map(c => ({ title: c.title, href: c.href, group: t.title, icon: t.icon }))),
  ...home.notes.filter(n => n.category === '工程实践').map(n => ({ title: n.title, href: n.href, group: n.category, icon: 'book' })),
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
      <nav class="jf-nav" aria-label="主导航"><a :href="withBase('/topics/')">专题</a><a href="#notes">笔记</a><a href="#about">关于</a></nav>
      <div class="jf-header-actions"><button class="jf-search" @click="openCommand" aria-label="打开快捷导航"><Icon name="search" :size="16" /><span>快捷导航</span><kbd>⌘ K</kbd></button><a class="jf-github" :href="home.github" target="_blank" rel="noopener noreferrer">GitHub <Icon name="arrow" :size="15" /></a><button class="jf-mobile-toggle" @click="menuOpen = !menuOpen" :aria-expanded="menuOpen" aria-label="切换导航菜单"><Icon :name="menuOpen ? 'close' : 'menu'" /></button></div>
      <nav v-if="menuOpen" class="jf-mobile-nav" aria-label="移动端导航"><a v-for="item in [['专题', withBase('/topics/')], ['笔记', '#notes'], ['关于', '#about']]" :href="item[1]" @click="menuOpen = false">{{ item[0] }}<Icon name="right" /></a><button @click="openCommand">快捷导航<Icon name="search" /></button></nav>
    </header>

    <main id="main">
      <section class="jf-hero jf-wrap" aria-labelledby="hero-heading">
        <div class="jf-hero-copy"><div class="jf-eyebrow"><span class="jf-live-dot"></span> PENGJIANG / LEARNING & LIFE</div>
          <h1 id="hero-heading">{{ home.headline[0] }}<br><span>{{ home.headline[1] }}</span></h1>
          <p class="jf-intro">{{ home.description }}</p>
          <div class="jf-hero-actions"><a class="jf-button jf-button-primary" href="#projects">浏览专题 <Icon name="right" :size="18" /></a><a class="jf-text-link" href="#notes">最近笔记 <Icon name="arrow" :size="16" /></a></div>
          <div class="jf-hero-note"><span class="jf-avatar">P<span></span></span><div><strong>AI 学习 · 理财笔记 · 兴趣档案</strong><span>LEARN · ORGANIZE · REVISIT</span></div></div>
        </div>
        <div class="jf-playground" aria-label="专题预览">
          <div class="jf-art-grid"></div><div class="jf-orb"><span></span></div><div class="jf-orbit jf-orbit-one"></div><div class="jf-orbit jf-orbit-two"></div><span class="jf-floating-dot"></span>
          <div class="jf-art-label"><span></span> INSIDE THE COLLECTIONS <span>↗</span></div>
          <div class="jf-preview">
            <div class="jf-window-bar"><span class="jf-window-dots"><i></i><i></i><i></i></span><span>workspace / {{ ['ai-learning', 'finance-notes', 'life-and-reading'][phase] }}</span><Icon name="code" :size="14" /></div>
            <div class="jf-preview-body" :key="phase">
              <div class="jf-preview-kicker">{{ topics[phase].en }}</div><h3>{{ topics[phase].title }}<span>↗</span></h3><p>{{ topics[phase].description }}</p><a :href="withBase(topics[phase].href)" class="jf-preview-link">{{ topics[phase].count }} · 开始阅读 <Icon name="right" :size="15" /></a>
            </div>
          </div>
          <div class="jf-phase-tabs" role="tablist" aria-label="创作阶段"><button v-for="(label, index) in phases" :key="label" role="tab" :aria-selected="phase === index" :class="{ active: phase === index }" @click="phase = index"><span>0{{ index + 1 }}</span>{{ label }}</button></div>
          <div class="jf-art-caption">Explore a topic. Follow a question. Keep a note.</div>
        </div>
      </section>
      <div class="jf-principles jf-wrap"><span>从好奇心出发</span><div><span><Icon name="code" :size="17" />用代码探索</span><span><Icon name="book" :size="17" />用文字沉淀</span><span><Icon name="sun" :size="17" />把过程分享</span></div><span class="jf-principles-end">ALWAYS A WORK IN PROGRESS ↗</span></div>

      <section id="projects" class="jf-section jf-wrap" aria-labelledby="projects-title"><div class="jf-section-heading"><div><span class="jf-section-label">01 / TOPIC COLLECTIONS</span><h2 id="projects-title">沿着主题，慢慢深入。</h2><p>从一篇笔记出发，逐步建立完整的理解。</p></div><a class="jf-text-link" :href="withBase('/topics/')">全部专题与章节 <Icon name="arrow" :size="16" /></a></div>
        <div class="jf-topic-cards"><a v-for="topic in topics" :key="topic.id" :href="withBase(topic.href)" class="jf-topic-card" :class="topic.color"><div class="jf-topic-card-top"><span class="jf-note-symbol" :class="topic.color"><Icon :name="topic.icon" :size="25" /></span><Icon name="arrow" :size="20" /></div><span class="jf-section-label">{{ topic.en }}</span><h3>{{ topic.title }}</h3><p>{{ topic.description }}</p><div class="jf-topic-card-bottom"><span>{{ topic.count }}</span><span>进入专题 →</span></div></a></div>
      </section>

      <section id="notes" class="jf-notes-section" aria-labelledby="notes-title"><div class="jf-wrap"><div class="jf-section-heading"><div><span class="jf-section-label">02 / FIELD NOTES</span><h2 id="notes-title">最近整理的内容。</h2><p>从专题导读到实践笔记，选择一个问题开始阅读。</p></div><div class="jf-filters" role="group" aria-label="筛选笔记"><button v-for="item in categories" :aria-pressed="category === item" :class="{ active: category === item }" @click="category = item">{{ item }}</button></div></div>
          <div class="jf-notes-grid" aria-live="polite"><a v-for="note in notes" :key="note.href" :href="href(note.href)" class="jf-note-card"><div class="jf-note-top"><span class="jf-note-symbol" :class="note.color"><Icon :name="note.tag === 'DEPLOYMENT' ? 'arrow' : note.tag === 'VITEPRESS' ? 'code' : 'book'" :size="21" /></span><span>{{ note.tag }}</span><Icon name="arrow" :size="19" /></div><h3>{{ note.title }}</h3><p>{{ note.description }}</p><div class="jf-note-meta"><span>{{ note.category }}</span><span><HeatCount :path="note.href" /> · {{ note.read }} <Icon name="right" :size="14" /></span></div></a></div>
        </div></section>

      <section id="about" class="jf-about jf-wrap" aria-labelledby="about-title"><div class="jf-about-left"><span class="jf-section-label">03 / A LITTLE ABOUT ME</span><h2 id="about-title">让知识有目录，<br>让记录有来处<span>。</span></h2></div><div class="jf-about-right"><p>这里是 PengJiang 的个人知识与生活记录空间。AI 专栏收录已有的系统学习调研，理财和兴趣专题从可复用的记录方法开始。</p><p>每篇内容保留清晰的主题和来源；长篇调研按章节阅读。也欢迎在文章下留下问题、补充资料和不同的理解。</p><a class="jf-text-link" :href="home.github" target="_blank" rel="noopener noreferrer">来 GitHub 找我 <Icon name="arrow" :size="17" /></a><div class="jf-about-signature">Notes, connected over time.</div></div></section>
    </main>
    <div class="jf-wrap"><PublicStats /></div>
    <footer class="jf-footer jf-wrap"><div><a class="jf-brand" href="#top">JFred<span class="jf-brand-dot">.</span></a><span>学习与生活，持续整理。</span></div><span>© {{ new Date().getFullYear() }} {{ home.author }} · <a :href="withBase('/privacy')">评论与统计说明</a></span><a href="#top">回到顶部 <span>↑</span></a></footer>

    <Teleport to="body"><div v-if="commandOpen" class="jf-command-overlay" @click.self="closeCommand"><section class="jf-command" ref="commandPanel" role="dialog" aria-modal="true" aria-labelledby="command-title"><h2 id="command-title" class="jf-sr-only">快捷导航</h2><div class="jf-command-input"><Icon name="search" /><input ref="searchInput" v-model="query" @input="activeResult = 0" placeholder="想去哪里？搜索页面或笔记…" aria-label="搜索页面或笔记" aria-controls="command-results" /><button @click="closeCommand" aria-label="关闭快捷导航">Esc</button></div><div class="jf-command-results" id="command-results"><span class="jf-command-label">{{ query ? '搜索结果' : '探索这个空间' }}</span><button v-for="(command, index) in commands" :id="`command-${index}`" :class="{ active: index === activeResult }" @mouseenter="activeResult = index" @click="choose(command.href)"><Icon :name="command.icon" :size="18" /><span>{{ command.title }}<small>{{ command.group }}</small></span><Icon name="enter" :size="16" /></button><p v-if="!commands.length" class="jf-no-results">没有找到相关内容，换一个关键词试试。</p></div><div class="jf-command-footer"><span><kbd>↑</kbd><kbd>↓</kbd> 选择</span><span><kbd>↵</kbd> 前往</span><span>JFred / 快捷导航</span></div></section></div></Teleport>
  </div>
</template>
