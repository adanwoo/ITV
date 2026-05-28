package com.iptv.player

import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.TextView
import androidx.recyclerview.widget.RecyclerView

class ChannelAdapter(
    private val channels: List<MainActivity.Channel>,
    private val onItemClick: (MainActivity.Channel, Int) -> Unit
) : RecyclerView.Adapter<ChannelAdapter.ViewHolder>() {

    private var selectedPosition = -1

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ViewHolder {
        val view = LayoutInflater.from(parent.context)
            .inflate(R.layout.item_channel, parent, false)
        return ViewHolder(view)
    }

    override fun onBindViewHolder(holder: ViewHolder, position: Int) {
        val channel = channels[position]
        holder.channelName.text = channel.name
        
        // 高亮当前播放的频道
        if (selectedPosition == position) {
            holder.itemView.setBackgroundColor(0x3300FF00)
            holder.playingIndicator.visibility = View.VISIBLE
        } else {
            holder.itemView.setBackgroundColor(0x00000000)
            holder.playingIndicator.visibility = View.GONE
        }
        
        holder.itemView.setOnClickListener {
            onItemClick(channel, position)
            setSelectedPosition(position)
        }
    }

    override fun getItemCount() = channels.size

    fun setSelectedPosition(position: Int) {
        val oldPos = selectedPosition
        selectedPosition = position
        notifyItemChanged(oldPos)
        notifyItemChanged(selectedPosition)
    }

    class ViewHolder(itemView: View) : RecyclerView.ViewHolder(itemView) {
        val channelName: TextView = itemView.findViewById(R.id.channel_name)
        val playingIndicator: View = itemView.findViewById(R.id.playing_indicator)
    }
}
